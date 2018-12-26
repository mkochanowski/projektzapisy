import { observable, action, flow, configure, computed } from "mobx";
import { clone } from "lodash";

import { Thesis, AppUser, ThesisTypeFilter } from "../types";
import {
	getThesesList, saveModifiedThesis, saveNewThesis,
	getCurrentUser, ThesesProcessParams, SortColumn, SortDirection, FAKE_USER,
} from "../backend_callers";
import { ApplicationState, ThesisWorkMode, canPerformBackendOp } from "../types/misc";
import { roundUp, awaitSleep } from "common/utils";

configure({ enforceActions: "observed" });

const ROWS_PER_PAGE = 30;

/** The currently selected thesis */
type CompositeThesis = {
	/** Its original, unchanged version */
	original: Thesis;
	/** And the version the user is modifying */
	modified: Thesis;
};

const enum LoadMode {
	Append,
	Replace,
}

class ThesesStore {
	@observable public theses: Thesis[] = [];
	@observable public thesis: CompositeThesis | null = null;
	@observable public lastRowIndex: number = 0;
	@observable public user: AppUser = FAKE_USER;
	@observable public applicationState: ApplicationState = ApplicationState.FirstLoad;
	@observable public fetchError: Error | null = null;
	@observable public workMode: ThesisWorkMode = ThesisWorkMode.Viewing;
	@observable public totalCount: number = 0;
	@observable public params: ThesesProcessParams = observable({
		type: ThesisTypeFilter.Default,
		title: "",
		advisor: "",
		sortColumn: SortColumn.None,
		sortDirection: SortDirection.Asc,
	});
	@observable public isChangingStringFilter: boolean;

	private onListChangedCallback: (() => void) | null = null;

	public registerOnListChanged(cb: () => void) {
		this.onListChangedCallback = cb;
	}

	public clearOnListChangedCallback() {
		this.onListChangedCallback = null;
	}

	@computed public get selectedIdx() {
		return thesisIndexInList(this.thesis && this.thesis.original, this.theses);
	}

	public initialize = flow(function* (this: ThesesStore) {
		this.user = yield getCurrentUser();
		yield this.refreshTheses();
		this.applicationState = ApplicationState.Normal;
	});

	private checkCanPerformBackendOp() {
		if (!canPerformBackendOp(this.applicationState)) {
			console.assert(false, "Not allowed to perform backend op");
			return false;
		}
		return true;
	}

	private refetch = flow(function*(this: ThesesStore) {
		this.applicationState = ApplicationState.Refetching;
		yield this.refreshTheses();
		this.applicationState = ApplicationState.Normal;
	});

	@action
	public onTypeFilterChanged = (value: ThesisTypeFilter) => {
		if (!this.checkCanPerformBackendOp()) {
			return;
		}
		this.params.type = value;
		this.refetch();
	}

	public onAdvisorFilterChanged = flow(function*(this: ThesesStore, value: string) {
		this.isChangingStringFilter = true;
		this.params.advisor = value.toLowerCase();
		yield this.refreshTheses();
		this.isChangingStringFilter = false;
	});

	public onTitleFilterChanged = flow(function*(this: ThesesStore, value: string) {
		this.isChangingStringFilter = true;
		this.params.title = value.toLowerCase();
		yield this.refreshTheses();
		this.isChangingStringFilter = false;
	});

	@action
	public onSortChanged = (column: SortColumn, dir: SortDirection) => {
		if (!this.checkCanPerformBackendOp()) {
			return;
		}
		this.params.sortColumn = column;
		this.params.sortDirection = dir;
		this.refetch();
	}

	public loadMore = flow(function* (this: ThesesStore, upToRow: number) {
		console.warn("render more", upToRow);
		if (!canPerformBackendOp(this.applicationState) || upToRow <= this.lastRowIndex) {
			return;
		}
		this.applicationState = ApplicationState.LoadingMore;
		yield this.loadTheses(LoadMode.Append, roundUp(upToRow, ROWS_PER_PAGE));
		this.applicationState = ApplicationState.Normal;
	});

	private refreshTheses() {
		return this.loadTheses(LoadMode.Replace, ROWS_PER_PAGE);
	}

	/** Download theses or set the error screen if an error occurred */
	private loadTheses = flow(function*(this: ThesesStore, mode: LoadMode, untilRow: number) {
		// Calling this function without having first set the state is an error
		console.assert(!canPerformBackendOp(this.applicationState));
		try {
			yield awaitSleep(3000);
			if (mode === LoadMode.Append) {
				console.assert(untilRow > this.lastRowIndex, "Already loaded");
				const result = yield getThesesList(
					this.params, this.lastRowIndex, untilRow - this.lastRowIndex,
				);
				this.theses = this.theses.concat(result.theses);
				this.totalCount = result.total;
			} else {
				const result = yield getThesesList(this.params, 0, untilRow);
				this.theses = result.theses;
				this.totalCount = result.total;
			}
			this.lastRowIndex = untilRow;
			if (this.onListChangedCallback) {
				this.onListChangedCallback();
			}
		} catch (err) {
			this.fetchError = err;
		}
	});

	@action
	public selectThesis(thesis: Thesis) {
		console.assert(
			this.theses.find(thesis.isEqual) != null,
			"Tried to select a nonexistent thesis",
		);
		this.workMode = ThesisWorkMode.Editing;
		this.thesis = compositeThesisForThesis(thesis);
	}

	public hasUnsavedChanges() {
		const { thesis } = this;
		return (
			thesis !== null &&
			!thesis.original.areValuesEqual(thesis.modified)
		);
	}

	@action
	public updateModifiedThesis = (thesis: Thesis) => {
		if (!this.thesis) {
			console.error("Modified nonexistent thesis");
			return;
		}
		this.thesis.modified = thesis;
	}

	@action
	public setupForNewThesis(thesis: Thesis) {
		this.workMode = ThesisWorkMode.Adding;
		this.thesis = compositeThesisForThesis(thesis);
	}

	@action
	public resetModifiedThesis() {
		console.assert(this.thesis != null);
		this.thesis = compositeThesisForThesis(this.thesis!.original);
	}

	private preSaveAsserts() {
		const { thesis, workMode } = this;
		if (thesis === null) {
			console.assert(false, "Tried to save thesis but none selected, this shouldn't happen");
			return false;
		}
		if (workMode === ThesisWorkMode.Viewing) {
			console.assert(false, "Tried to perform a save action when only viewing");
			return false;
		}
		if (!this.hasUnsavedChanges()) {
			console.assert(false, "save() called but no unsaved changes");
			return false;
		}
		if (!canPerformBackendOp(this.applicationState)) {
			console.assert(false, "Called save() but we're already doing something backend-related");
			return false;
		}
		return true;
	}

	private handlerForWorkMode = {
		[ThesisWorkMode.Adding]: addNewThesis,
		[ThesisWorkMode.Editing]: modifyExistingThesis,
	};

	public save = flow(function*(this: ThesesStore) {
		if (!this.preSaveAsserts()) {
			return;
		}

		const { workMode, thesis } = this;

		this.applicationState = ApplicationState.Saving;
		type NonViewModes = (ThesisWorkMode.Adding | ThesisWorkMode.Editing);
		const handler = this.handlerForWorkMode[workMode as NonViewModes];

		let id: number;
		try {
			id = yield handler(thesis!);
		} catch (err) {
			this.applicationState = ApplicationState.Normal;
			throw err;
		}

		yield this.refreshTheses();

		const toSelect = this.theses.find(t => t.id === id) || null;
		this.applicationState = ApplicationState.Normal;
		// no matter what the work mode was, if we have a thesis we end up in the edit view
		this.thesis = compositeThesisForThesis(toSelect);
	});
}

async function modifyExistingThesis(thesis: CompositeThesis) {
	await saveModifiedThesis(thesis.original, thesis.modified);
	return thesis!.original.id;
}

function addNewThesis(thesis: CompositeThesis) {
	return saveNewThesis(thesis.modified);
}

function thesisIndexInList(thesis: Thesis | null, theses: Thesis[]) {
	return thesis
		? theses.findIndex(thesis.isEqual)
		: -1;
}

function compositeThesisForThesis(t: Thesis | null) {
	return t ? { original: t, modified: clone(t) } : null;
}

const thesesStore = new ThesesStore();
export { thesesStore };
