/**
 * @file Misc utils for the thesis system app.
 */

import * as React from "react";

/**
 * Returns a style object to be applied to "disabled" components.
 * Certain components in the app can enter a "disabled" state;
 * they will then apply this CSS to visually indicate this to the user.
 */
export function getDisabledStyle(): React.CSSProperties {
	return { opacity: 0.5, pointerEvents: "none" };
}

// Update the top-menu indicator (the Django template formats it properly,
// but the theses app uses asynchronous requests to save votes, so we need
// to do it manually here too)
export function adjustDomForUngraded(numUngraded: number): void {
	const elem = document.getElementById("num_ungraded_theses");
	if (!elem) {
		console.error("adjustDomForUngraded: element not found");
		return;
	}
	elem.textContent = numUngraded ? ` (${numUngraded})` : "";
}
