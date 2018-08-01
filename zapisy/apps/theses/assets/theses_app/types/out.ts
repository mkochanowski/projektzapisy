// Types we'll be dispatching to the Python backend to perform changes

import { ThesisKind, ThesisStatus, Thesis, BasePerson } from ".";

export type PersonOutJson = {
	id: number;
};

export type ThesisOutJson = {
	id: number;
	title?: string;
	advisor?: PersonOutJson | null;
	auxiliary_advisor?: PersonOutJson | null;
	kind?: ThesisKind;
	reserved?: boolean;
	description?: string;
	status?: ThesisStatus;
	student?: PersonOutJson | null;
	student_2?: PersonOutJson | null;
	modified_date?: string;
};

function getNewPersonValue(
	originalPersonField: BasePerson | null,
	modifiedPersonField: BasePerson | null,
) {
	if (originalPersonField) {
		if (modifiedPersonField) {
			if (originalPersonField.id !== modifiedPersonField.id) {
				return { changed: true, id: modifiedPersonField.id };
			}
			return { changed: false };
		} else {
			return { changed: true, id: null };
		}
	}
	if (modifiedPersonField) {
		return { changed: true, id: modifiedPersonField.id };
	}
	return { changed: false };
}

export function getOutThesisJson(originalThesis: Thesis, modifiedThesis: Thesis): ThesisOutJson {
	console.assert(originalThesis.id === modifiedThesis.id);
	const result: ThesisOutJson = {
		id: originalThesis.id,
	};
	if (originalThesis.title !== modifiedThesis.title) {
		result.title = modifiedThesis.title;
	}
	let changed; let id;
	({ changed, id } = getNewPersonValue(originalThesis.advisor, modifiedThesis.advisor));
	// if (changed) { result.advisor = id; }

	return result;
}
