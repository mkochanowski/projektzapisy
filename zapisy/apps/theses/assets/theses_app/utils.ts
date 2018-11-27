import * as React from "react";

import { Thesis } from "./types";

export function isThesisAvailable(thesis: Thesis): boolean {
	return !thesis.reserved; // TODO status?
}

export function getDisabledStyle(): React.CSSProperties {
	return { opacity: 0.5, pointerEvents: "none" };
}
