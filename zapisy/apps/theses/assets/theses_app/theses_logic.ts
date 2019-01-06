/**
 * @file Stores application data and implements theses fetching/editing
 * logic by interacting with lower-level APIs from backend_callers
 * Conceptually ThesesApp is responsible for rendering the entire application
 * and imports logic manipulation functions from this file, passing them
 * as props to subcomponents so that they can change global application state
 */
import { observable, action, flow, configure, computed } from "mobx";
import { clone } from "lodash";

import {
	getThesesList, saveModifiedThesis, saveNewThesis,
	getCurrentUser, getThesesBoard, FAKE_USER,
} from "./backend_callers";
import {
	ApplicationState, ThesisWorkMode, isPerformingBackendOp,
	ThesesProcessParams, SortColumn, SortDirection,
} from "./app_types";
import { roundUp, wait } from "common/utils";
import { CancellablePromise } from "mobx/lib/api/flow";
import { ThesisEmptyTitle } from "./errors";
import { Thesis } from "./thesis";
import { ThesisTypeFilter, UserType } from "./protocol_types";
import { AppUser, Employee, Person } from "./users";

/** Tell MobX to ensure that @observable fields are only modified in actions */
configure({ enforceActions: "observed" });

/** How many theses to download in a single request */
const ROWS_PER_PAGE = 100;

/**
 * How long to wait after the last keystroke before dispatching
 * a request to the backend with the specified filter
 * This assumes the user will be typing at at least 240 CPM
 * which is slightly above average, but our target audience is rather
 * more computer literate than the average person, so that should be fine
 */
const STRING_FILTER_QUERY_DELAY = 250;

/** The currently selected thesis */
type CompositeThesis = {
	/** Its original, unchanged version */
	original: Thesis;
	/** And the version the user is modifying */
	modified: Thesis;
};

/** The mode in which we're loading theses:
 * should we append them at the end, or replace the entire list?
 */
export const enum LoadMode {
	Append,
	Replace,
}

/** Which string filter (above the table) is being changed? */
export type ChangedStringFilter = "advisor" | "title" | "";

class ThesesStore {
	/** All the theses we currently know about (having downloaded them from the backend) */
	@observable public theses: Thesis[] = [];
	@observable public thesis: CompositeThesis | null = null;
	@observable public thesesBoard: Employee[] = [];
	/** The last thesis row we have downloaded */
	@observable private lastRowIndex: number = 0;
	@observable public user: AppUser = FAKE_USER;
	@observable public applicationState: ApplicationState = ApplicationState.FirstLoad;
	/** Work state: just viewing, modifying an existing one or adding a new one */
	@observable public workMode: ThesisWorkMode = ThesisWorkMode.Viewing;
	/** The total number of theses matching current filters.
	 * Note that this will almost always be more than theses.length - theses
	 * only holds a subset of everything that's available, unless the user
	 * scrolls to the very end
	 */
	@observable public totalCount: number = 0;
	/** Current filtering/sort params */
	@observable public params: ThesesProcessParams = observable({
		type: ThesisTypeFilter.Default,
		onlyMine: false,
		title: "",
		advisor: "",
		sortColumn: SortColumn.None,
		sortDirection: SortDirection.Asc,
	});
	@observable public stringFilterBeingChanged: ChangedStringFilter = "";
	/** Represents the current asynchronous filter edition action */
	private stringFilterPromise: CancellablePromise<any> | null = null;

	/** Other parts of the system need to be told whenever the list changes */
	private onListChangedCallback: ((mode: LoadMode) => void) | null = null;
	public registerOnListChanged(cb: (mod: LoadMode) => void) {
		this.onListChangedCallback = cb;
	}
	public clearOnListChanged() {
		this.onListChangedCallback = null;
	}

	private onErrorCallback: ((err: Error) => void) | null = null;
	public registerOnError(cb: (err: Error) => void) {
		this.onErrorCallback = cb;
	}
	public clearOnError() {
		this.onErrorCallback = null;
	}
	/** Handle an internal fatal error that occurred in the store.
	 * The main component is expected to install a callback so that
	 * it can be told about the error and display it
	 */
	private handleError(err: Error) {
		if (this.onErrorCallback) {
			this.onErrorCallback(err);
		} else {
			console.error("Error while loading and no callback:", err);
		}
	}

	/** The position of the currently selected thesis in the list */
	@computed public get selectedIdx() {
		return thesisIndexInList(this.thesis && this.thesis.original, this.theses);
	}

	public initialize = flow(function* (this: ThesesStore) {
		try {
			this.user = yield getCurrentUser();
			this.thesesBoard = yield getThesesBoard();
			if (this.user.type === UserType.Employee && !this.isThesesBoardMember(this.user.user)) {
				// employees are most likely only interested in their own theses
				this.params.onlyMine = true;
			}
			yield this.refreshTheses();
			this.applicationState = ApplicationState.Normal;
		} catch (err) {
			this.handleError(err);
		}
	});

	/**
	 * Checks whether the given user is a member of the theses board
	 */
	public isThesesBoardMember(user: Person): boolean {
		return !!this.thesesBoard.find(member => member.isEqual(user));
	}

	private checkCanPerformBackendOp() {
		if (isPerformingBackendOp(this.applicationState)) {
			console.assert(false, "Not allowed to perform backend op");
			return false;
		}
		return true;
	}

	/** Re-download theses from the backend respecting current params */
	private refetch = flow(function*(this: ThesesStore) {
		this.applicationState = ApplicationState.Refetching;
		yield this.refreshTheses();
		this.applicationState = ApplicationState.Normal;
	});

	@action
	public onTypeFilterChanged(value: ThesisTypeFilter) {
		if (!this.checkCanPerformBackendOp()) {
			return;
		}
		this.params.type = value;
		this.refetch();
	}

	@action
	public onOnlyMineChanged(value: boolean) {
		if (!this.checkCanPerformBackendOp()) {
			return;
		}
		this.params.onlyMine = value;
		this.refetch();
	}

	// Regarding the next two functions: see https://mobx.js.org/best/actions.html
	// (the flow section at the bottom)

	/** Save the new filter value, wait for the user to maybe type more,
	 * after the set delay assume they won't and query the backend
	 */
	private changeStringFilterInternal = flow(function*(
		this: ThesesStore, thisKey: "title" | "advisor", value: string
	) {
		this.params[thisKey] = value.toLowerCase();
		this.stringFilterBeingChanged = thisKey;
		this.applicationState = ApplicationState.Refetching;
		yield wait(STRING_FILTER_QUERY_DELAY);
		yield this.refreshTheses();
		this.applicationState = ApplicationState.Normal;
		this.stringFilterBeingChanged = "";
		// a suicide of sorts
		this.stringFilterPromise = null;
	});

	@action
	private changeStringFilter(
		thisKey: "title" | "advisor", otherKey: "title" | "advisor",
		value: string
	) {
		if (this.stringFilterBeingChanged === otherKey) {
			console.assert(false, "Not allowed");
			return;
		}
		// If a string filter action is already going on, it should be
		// cancelled - we won't be interested in the old results anyway,
		// since the filter value changed
		if (this.stringFilterPromise) {
			console.assert(this.stringFilterBeingChanged === thisKey);
			this.stringFilterPromise.cancel();
		}
		const changePromise = this.changeStringFilterInternal(thisKey, value);
		changePromise.catch(err => {
			// This is the error thrown in the promise when we call cancel()
			// so that's expected; anything else is a real error
			if (!err.toString().includes("FLOW_CANCELLED")) {
				console.error("When attempting to fetch filtered results:", err);
			}
		});
		this.stringFilterPromise = changePromise;
	}

	public onAdvisorFilterChanged(value: string) {
		this.changeStringFilter("advisor", "title", value);
	}

	public onTitleFilterChanged(value: string) {
		this.changeStringFilter("title", "advisor", value);
	}

	@action
	public onSortChanged(column: SortColumn, dir: SortDirection) {
		if (!this.checkCanPerformBackendOp()) {
			return;
		}
		this.params.sortColumn = column;
		this.params.sortDirection = dir;
		this.refetch();
	}

	/** Load more rows as demanded by the table component */
	public loadMore = flow(function* (this: ThesesStore, upToRow: number) {
		// The table component might call this function many times in response
		// to the same scroll "session"
		if (isPerformingBackendOp(this.applicationState) || upToRow <= this.lastRowIndex) {
			return;
		}
		this.applicationState = ApplicationState.LoadingMore;
		yield this.loadTheses(LoadMode.Append, roundUp(upToRow, ROWS_PER_PAGE));
		this.applicationState = ApplicationState.Normal;
	});

	/** Download rows in range 0 - ROWS_PER_PAGE, replacing the current set */
	private refreshTheses() {
		return this.loadTheses(LoadMode.Replace, ROWS_PER_PAGE);
	}

	/**
	 * Download theses from the backend
	 * @param mode The mode in which to perform the action - replace or append new rows
	 * @param untilRow Ensure that all rows up to this one are available
	 */
	private loadTheses = flow(function*(this: ThesesStore, mode: LoadMode, untilRow: number) {
		// Calling this function without having first set the state is an error
		console.assert(isPerformingBackendOp(this.applicationState));
		try {
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
				this.onListChangedCallback(mode);
			}
		} catch (err) {
			this.handleError(err);
		}
	});

	/**
	 * Set the specified thesis as selected
	 * @param thesis The thesis to select; must be in the local theses list
	 */
	@action
	public selectThesis(thesis: Thesis) {
		console.assert(
			this.theses.find(thesis.isEqual) != null,
			"Tried to select a nonexistent thesis",
		);
		this.workMode = ThesisWorkMode.Editing;
		this.thesis = compositeThesisForThesis(thesis);
	}

	/** Determine whether we have a thesis being modified and if so,
	 * whether it's different from the original one
	 */
	public hasUnsavedChanges() {
		const { thesis } = this;
		return (
			thesis !== null &&
			!thesis.original.areValuesEqual(thesis.modified)
		);
	}

	/**
	 * Update the modified thesis instance (it's an immutable object, a new instance
	 * must be set)
	 * @param thesis The new modified instance
	 */
	@action
	public updateModifiedThesis(thesis: Thesis) {
		if (!this.thesis) {
			console.error("Modified nonexistent thesis");
			return;
		}
		this.thesis.modified = thesis;
	}

	/**
	 * Set the specified thesis as active and switch to adding mode
	 * @param thesis The thesis we'll be adding
	 */
	@action
	public setupForNewThesis(thesis: Thesis) {
		this.workMode = ThesisWorkMode.Adding;
		this.thesis = compositeThesisForThesis(thesis);
	}

	/**
	 * Discard all changes in the modified instance, resetting it to original
	 */
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
		if (isPerformingBackendOp(this.applicationState)) {
			console.assert(false, "Called save() but we're already doing something backend-related");
			return false;
		}
		return true;
	}

	private performPreSaveChecks() {
		const { modified } = this.thesis!;
		const trimmedTitle = modified.title.trim();
		if (!trimmedTitle) {
			throw new ThesisEmptyTitle();
		}
	}

	private handlerForWorkMode = {
		[ThesisWorkMode.Adding]: addNewThesis,
		[ThesisWorkMode.Editing]: modifyExistingThesis,
	};

	/**
	 * Save the currently selected thesis. It is an error to call this
	 * if there are no unsaved changes.
	 */
	public save = flow(function*(this: ThesesStore) {
		if (!this.preSaveAsserts()) {
			return;
		}
		this.performPreSaveChecks();

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

		// Reload without losing the current position
		yield this.loadTheses(LoadMode.Replace, this.lastRowIndex);

		const toSelect = this.theses.find(t => t.id === id) || null;
		this.applicationState = ApplicationState.Normal;
		// no matter what the work mode was, if we have a thesis we end up in the edit view
		this.workMode = toSelect ? ThesisWorkMode.Editing : ThesisWorkMode.Viewing;
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
