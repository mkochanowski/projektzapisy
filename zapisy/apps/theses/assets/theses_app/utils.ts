/*
	Misc utils for the thesis system app.
*/

import * as React from "react";

import { Thesis } from "./types";

// Should the given thesis be marked as "available" in the UI?
// This is mostly used when filtering theses by type in the list.
export function isThesisAvailable(thesis: Thesis): boolean {
	return !thesis.reserved;
}

// Certain components in the app can enter a "disabled" state;
// they will then apply this CSS to visually indicate this to the user.
export function getDisabledStyle(): React.CSSProperties {
	return { opacity: 0.5, pointerEvents: "none" };
}
