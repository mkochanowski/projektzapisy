/*
	Miscellaneous types
*/

// The current global application mode
export const enum ApplicationState {
	InitialLoading,
	PerformingBackendChanges,
	Normal,
}

// Are we editing an existing thesis or adding a new one?
export const enum ThesisWorkMode {
	Editing,
	Adding,
}
