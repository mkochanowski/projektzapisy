import { AppUser, UserType, Thesis, Employee } from "./types";

export function canAddThesis(user: AppUser) {
	return user.type !== UserType.Student;
}

function isThesisStaff(user: AppUser) {
	return [UserType.Admin, UserType.ThesesBoardMember].includes(user.type);
}

export function canCastVoteAsUser(appUser: AppUser, user: Employee) {
	return appUser.type === UserType.Admin || appUser.user.isEqual(user);
}

export function canModifyThesis(user: AppUser, thesis: Thesis) {
	return (
		isThesisStaff(user) ||
		user.type === UserType.Employee &&
		thesis.advisor !== null &&
		thesis.advisor.id === user.user.id
	);
}

export function canChangeStatus(user: AppUser) {
	return isThesisStaff(user);
}

export function canSetArbitraryAdvisor(user: AppUser) {
	return isThesisStaff(user);
}
