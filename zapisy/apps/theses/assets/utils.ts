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
