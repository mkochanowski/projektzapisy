import { observable, action, flow, configure, computed } from "mobx";
import { clone } from "lodash";

import { Thesis, AppUser, ThesisTypeFilter } from "../types";
import {
	getThesesList, saveModifiedThesis, saveNewThesis,
	getCurrentUser, ThesesProcessParams, SortColumn, SortDirection, FAKE_USER,
} from "../backend_callers";
import { ApplicationState, ThesisWorkMode } from "../types/misc";

configure({ enforceActions: "observed" });

const ROWS_PER_PAGE = 30;

/** The currently selected thesis */
type CompositeThesis = {
	/** Its original, unchanged version */
	original: Thesis;
	/** And the version the user is modifying */
	modified: Thesis;
};

class ThesesStore {
	@observable public theses: Thesis[] = [];
	@observable public thesis: CompositeThesis | null = null;
	@observable public currentPage: number = 1;
	@observable public user: AppUser = FAKE_USER;
	@observable public applicationState: ApplicationState = ApplicationState.InitialLoading;
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

	@computed public get selectedIdx() {
		return thesisIndexInList(this.thesis && this.thesis.original, this.theses);
	}

	public initialize = flow(function* (this: ThesesStore) {
		this.user = yield getCurrentUser();
		yield this.refreshTheses();
		this.applicationState = ApplicationState.Normal;
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

	private disableAndRefetch = flow(function*(this: ThesesStore) {
		this.currentPage = 1;
		this.applicationState = ApplicationState.FetchingTheses;
		yield this.refreshTheses();
		this.applicationState = ApplicationState.Normal;
	});

	private refetch() {
		this.currentPage = 1;
		this.refreshTheses();
	}

	@action
	public onTypeFilterChanged = (value: ThesisTypeFilter) => {
		this.params.type = value;
		this.disableAndRefetch();
	}
	@action
	public onAdvisorFilterChanged = (value: string) => {
		this.params.advisor = value.toLowerCase();
		this.refetch();
	}
	@action
	public onTitleFilterChanged = (value: string) => {
		this.params.title = value.toLowerCase();
		this.refetch();
	}

	@action
	public onSortChanged = (column: SortColumn, dir: SortDirection) => {
		this.params.sortColumn = column;
		this.params.sortDirection = dir;
		this.disableAndRefetch();
	}

	public loadMore = flow(function* (this: ThesesStore, until: number) {
		console.warn("render more", until);
		const page = indexToPage(until);
		if (page <= this.currentPage) {
			return;
		}
		this.currentPage = page;
		yield this.refreshTheses();
	});

	/** Download theses or set the error screen if an error occurred */
	public refreshTheses = flow(function*(this: ThesesStore) {
		try {
			const result = yield getThesesList(this.params, this.currentPage);
			if (this.currentPage === 1) {
				this.theses = result.theses;
			} else {
				this.theses = this.theses.concat(result.theses);
			}
			this.totalCount = result.total;
		} catch (err) {
			this.fetchError = err;
		}
	});

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

		this.currentPage = 1;
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

function indexToPage(index: number) {
	return Math.ceil(index / ROWS_PER_PAGE);
}

function compositeThesisForThesis(t: Thesis | null) {
	return t ? { original: t, modified: clone(t) } : null;
}

const thesesStore = new ThesesStore();
export { thesesStore };
