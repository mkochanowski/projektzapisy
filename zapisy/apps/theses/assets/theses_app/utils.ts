import { Thesis } from "./types";

export function isThesisAvailable(thesis: Thesis): boolean {
	return !thesis.reserved; // TODO status?
}
