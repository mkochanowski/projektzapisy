import { ThesisTypeFilter } from ".";

/**
 * @file Miscellaneous types
 */

/**
 * The current global application mode
 */
export const enum ApplicationState {
	FirstLoad,
	LoadingMore,
	Refetching,
	Saving,
	Normal,
}

export function isPerformingBackendOp(state: ApplicationState) {
	return state !== ApplicationState.Normal;
}

/**
 * Determines whether we're adding a new thesis or modifying an existing one
 */
export const enum ThesisWorkMode {
	Viewing,
	Editing,
	Adding,
}

export const enum SortDirection {
	Asc,
	Desc,
}
export const enum SortColumn {
	None,
	Advisor,
	Title,
}

/**
 * Thesis processing parameters - filters and sorting
 */
export type ThesesProcessParams = {
	advisor: string;
	title: string;
	type: ThesisTypeFilter;

	sortColumn: SortColumn;
	sortDirection: SortDirection;
};
