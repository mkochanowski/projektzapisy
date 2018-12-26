/**
 * @file Miscellaneous types
 */

/**
 * The current global application mode
 */
export const enum ApplicationState {
	InitialLoading,
	PerformingBackendChanges,
	Normal,
}

/**
 * Determines whether we're adding a new thesis or modifying an existing one
 */
export const enum ThesisWorkMode {
	Viewing,
	Editing,
	Adding,
}
