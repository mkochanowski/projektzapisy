/**
 * @file Theses app permission checks, mostly analogous to permissions.py
 */
import { AppUser, UserType, Thesis, ThesisStatus } from "./types";
import { thesesStore } from "./theses_store";

/**
 * Determine whether the specified app user has a thesis staff role
 * @param user The app user
 */
function isThesisStaff(user: AppUser) {
	return user.type === UserType.Admin || thesesStore.isThesesBoardMember(user.user);
}

/**
 * Determine whether the specified app user is permitted to add new objects
 * @param user The app user
 */
export function canAddThesis(user: AppUser) {
	return user.type !== UserType.Student;
}

/**
 * Determine whether the specified user "owns" the specified thesis
 * @param user The app user
 * @param thesis The thesis
 */
function isOwnerOfThesis(user: AppUser, thesis: Thesis) {
	return (
		thesis.advisor !== null &&
		user.type === UserType.Employee &&
		thesis.advisor.id === user.user.id
	);
}

/**
 * Determine if the specified user is permitted to make any changes to the specified thesis
 * @param user The user
 * @param thesis The thesis
 */
export function canModifyThesis(user: AppUser, thesis: Thesis) {
	return (
		isThesisStaff(user) ||
		user.type === UserType.Employee &&
		isOwnerOfThesis(user, thesis)
	);
}

/**
 * Determine if the specified user is permitted to change the title of the specified thesis
 * @param user The user
 * @param thesis The thesis
 */
export function canChangeTitle(user: AppUser, thesis: Thesis) {
	const frozenStatuses = [
		ThesisStatus.Accepted, ThesisStatus.Defended, ThesisStatus.InProgress,
	];
	return (
		isThesisStaff(user) ||
		isOwnerOfThesis(user, thesis) && !frozenStatuses.includes(thesis.status)
	);
}

/**
 * Determine if a user of the specified type can modify an existing thesis' status
 * @param user The app user
 */
export function canChangeStatus(user: AppUser) {
	return isThesisStaff(user);
}

/**
 * Determine if the specified user is allowed to set any advisor on any thesis
 * @param user The app user
 */
export function canSetArbitraryAdvisor(user: AppUser) {
	return isThesisStaff(user);
}