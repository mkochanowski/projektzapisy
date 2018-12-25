/**
 * Defines types that will be dispatched to the backend
 * as well as functions to operate on them
 */
import { ThesisKind, ThesisStatus, Thesis, BasePerson, MAX_THESIS_TITLE_LEN } from ".";

/**
 * The representation of a person sent to the backend
 */
export type PersonDispatch = {
	id: number;
};

/**
 * The representation of a new thesis object sent to the backend
 */
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

/**
 * The representation of a diff for an existing thesis object sent to the backend
 */
export type ThesisModDispatch = {
	id: number;
} & ThesisAddDispatch;

/**
 * Given a new thesis object, convert it to a representation
 * consumed by the backend
 * @param thesis The thesis object to convert
 */
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

/**
 * Given an old and new person value, determine whether it should be considered
 * to have "changed" - based on this we will include it in the info sent to the backend
 */
function hadPersonChange(old: BasePerson | null, newp: BasePerson | null) {
	return (
		old === null && newp !== null ||
		old !== null && newp === null ||
		old !== null && newp !== null && !old.isEqual(newp)
	);
}

/**
 * Given a person instance, convert it to the backend representation
 */
function toPersonDispatch(newPerson: BasePerson | null): PersonDispatch | null {
	return newPerson ? { id: newPerson.id } : null;
}

/**
 * Given the previous and new thesis object, compute the diff to be
 * sent to the backend
 * @param orig The old thesis object
 * @param mod The new (modified) thesis object
 */
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
