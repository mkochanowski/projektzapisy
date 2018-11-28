// Types we'll be dispatching to the Python backend to perform changes

import { ThesisKind, ThesisStatus, Thesis, BasePerson } from ".";

export type PersonDispatch = {
	id: number;
};

export type ThesisDispatch = {
	id: number;
	title?: string;
	advisor?: PersonDispatch | null;
	auxiliary_advisor?: PersonDispatch | null;
	kind?: ThesisKind;
	reserved?: boolean;
	description?: string;
	status?: ThesisStatus;
	student?: PersonDispatch | null;
	student_2?: PersonDispatch | null;
	modified_date?: string;
};

function getNewPersonValue(
	originalPersonField: BasePerson | null,
	modifiedPersonField: BasePerson | null,
) {
	console.warn(originalPersonField, modifiedPersonField);
	if (originalPersonField) {
		if (modifiedPersonField) {
			if (originalPersonField.id !== modifiedPersonField.id) {
				return { id: modifiedPersonField.id };
			}
		} else {
			return null;
		}
	} else if (modifiedPersonField) {
		return { id: modifiedPersonField.id };
	}
}

export function getThesisDispatch(originalThesis: Thesis, modifiedThesis: Thesis): ThesisDispatch {
	originalThesis.isEqual(modifiedThesis);
	const result: ThesisDispatch = {
		id: originalThesis.id,
	};
	if (originalThesis.title !== modifiedThesis.title) {
		result.title = modifiedThesis.title;
	}
	result.advisor = getNewPersonValue(originalThesis.advisor, modifiedThesis.advisor);
	result.auxiliary_advisor = getNewPersonValue(
		originalThesis.auxiliaryAdvisor, modifiedThesis.auxiliaryAdvisor,
	);
	result.student = getNewPersonValue(originalThesis.student, modifiedThesis.student);
	result.student_2 = getNewPersonValue(originalThesis.secondStudent, modifiedThesis.secondStudent);
	if (originalThesis.kind !== modifiedThesis.kind) {
		result.kind = modifiedThesis.kind;
	}
	if (originalThesis.reserved !== modifiedThesis.reserved) {
		result.reserved = modifiedThesis.reserved;
	}
	if (originalThesis.description !== modifiedThesis.description) {
		result.description = modifiedThesis.description;
	}
	if (originalThesis.status !== modifiedThesis.status) {
		result.status = modifiedThesis.status;
	}

	return result;
}
