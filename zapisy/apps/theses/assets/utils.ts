/**
 * @file Misc utils for the thesis system app.
 */

import * as React from "react";
import { Moment } from "moment";

/**
 * Returns a style object to be applied to "disabled" components.
 * Certain components in the app can enter a "disabled" state;
 * they will then apply this CSS to visually indicate this to the user.
 */
export function getDisabledStyle(): React.CSSProperties {
	return { opacity: 0.5, pointerEvents: "none" };
}

/**
 * Format a given moment instance to string.
 */
export function formatDate(m: Moment): string {
	return m.format("DD/MM/YYYY HH:mm:ss");
}

/**
 * Determine whether two nullable values are equal
 * @param val1 The first value
 * @param val2 The second value
 * @param compare The comparator used when both values are nonnull
 */
export function nullableValuesEqual<T>(
	val1: T | null, val2: T | null, compare: (v1: T, v2: T) => boolean
): boolean {
	return (
		val1 === null && val2 === null ||
		val1 !== null && val2 !== null && compare(val1, val2)
	);
}
