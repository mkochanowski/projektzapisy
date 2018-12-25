/*
	Theses app permission checks, analogous to permissions.py
*/

import { AppUser, UserType, Thesis, ThesisStatus } from "./types";

// Is this user a theses staff member, that is the system admin or a board member?
function isThesisStaff(user: AppUser) {
	return [UserType.Admin, UserType.ThesesBoardMember].includes(user.type);
}

// Is the given user permitted to add new thesis objects?
export function canAddThesis(user: AppUser) {
	return user.type !== UserType.Student;
}

// Is the specified user the advisor of the specified thesis?
function isOwnerOfThesis(user: AppUser, thesis: Thesis) {
	return thesis.advisor !== null && thesis.advisor.id === user.user.id;
}

// Is the specified user permitted to make any changes to the specified thesis?
export function canModifyThesis(user: AppUser, thesis: Thesis) {
	return (
		isThesisStaff(user) ||
		user.type === UserType.Employee &&
		isOwnerOfThesis(user, thesis)
	);
}

// Is the specified user permitted to change the title of the specified thesis?
export function canChangeTitle(user: AppUser, thesis: Thesis) {
	return (
		isThesisStaff(user) ||
		isOwnerOfThesis(user, thesis) && thesis.status !== ThesisStatus.Accepted
	);
}

// Can a user of the specified type modify an existing thesis' status?
export function canChangeStatus(user: AppUser) {
	return isThesisStaff(user);
}

// Is the specified user allowed to set any advisor on any thesis?
export function canSetArbitraryAdvisor(user: AppUser) {
	return isThesisStaff(user);
}
