/**
 * @file Miscellaneous types
 */

/**
 * The current global application mode
 */
export const enum ApplicationState {
	InitialLoading,
	FetchingTheses,
	Saving,
	Normal,
}

export function isWaitingOnBackend(state: ApplicationState) {
	return [
		ApplicationState.Saving, ApplicationState.FetchingTheses,
	].includes(state);
}

/**
 * Determines whether we're adding a new thesis or modifying an existing one
 */
export const enum ThesisWorkMode {
	Viewing,
	Editing,
	Adding,
}
