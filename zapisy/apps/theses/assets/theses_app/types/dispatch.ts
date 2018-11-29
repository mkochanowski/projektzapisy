// Types we'll be dispatching to the Python backend to perform changes

import { ThesisKind, ThesisStatus, Thesis, BasePerson, MAX_THESIS_TITLE_LEN } from ".";

export type PersonDispatch = {
	id: number;
};

export type ThesisAddDispatch = {
	title?: string;
	advisor?: PersonDispatch | null;
	auxiliary_advisor?: PersonDispatch | null;
	kind?: ThesisKind;
	reserved?: boolean;
	description?: string;
	status?: ThesisStatus;
	student?: PersonDispatch | null;
	student_2?: PersonDispatch | null;
};

export type ThesisModDispatch = {
	id: number;
} & ThesisAddDispatch;

export function getThesisAddDispatch(thesis: Thesis): ThesisAddDispatch {
	const result: ThesisAddDispatch = {
		title: thesis.title,
		kind: thesis.kind,
		reserved: thesis.reserved,
		description: thesis.description,
		status: thesis.status,
	};
	if (thesis.advisor) {
		result.advisor = toPersonDispatch(thesis.advisor);
	}
	if (thesis.auxiliaryAdvisor) {
		result.auxiliary_advisor = toPersonDispatch(thesis.auxiliaryAdvisor);
	}
	if (thesis.student) {
		result.student = toPersonDispatch(thesis.student);
	}
	if (thesis.secondStudent) {
		result.student_2 = toPersonDispatch(thesis.secondStudent);
	}
	return result;
}

function hadPersonChange(old: BasePerson | null, newp: BasePerson | null) {
	return (
		old === null && newp !== null ||
		old !== null && newp === null ||
		old !== null && newp !== null && !old.isEqual(newp)
	);
}

function toPersonDispatch(newPerson: BasePerson | null): PersonDispatch | null {
	return newPerson ? { id: newPerson.id } : null;
}

export function getThesisModDispatch(orig: Thesis, mod: Thesis): ThesisModDispatch {
	console.assert(orig.isEqual(mod));
	const result: ThesisModDispatch = { id: orig.id };
	if (orig.title !== mod.title) {
		result.title = mod.title.slice(0, MAX_THESIS_TITLE_LEN);
	}
	if (hadPersonChange(orig.advisor, mod.advisor)) {
		result.advisor = toPersonDispatch(mod.advisor);
	}
	if (hadPersonChange(orig.auxiliaryAdvisor, mod.auxiliaryAdvisor)) {
		result.auxiliary_advisor = toPersonDispatch(mod.auxiliaryAdvisor);
	}
	if (hadPersonChange(orig.student, mod.student)) {
		result.student = toPersonDispatch(mod.student);
	}
	if (hadPersonChange(orig.secondStudent, mod.secondStudent)) {
		result.student_2 = toPersonDispatch(mod.secondStudent);
	}
	if (orig.kind !== mod.kind) {
		result.kind = mod.kind;
	}
	if (orig.reserved !== mod.reserved) {
		result.reserved = mod.reserved;
	}
	if (orig.description !== mod.description) {
		result.description = mod.description;
	}
	if (orig.status !== mod.status) {
		result.status = mod.status;
	}

	return result;
}
