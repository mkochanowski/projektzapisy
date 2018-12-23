import { AppUser, UserType, Thesis, ThesisStatus } from "./types";

export function canAddThesis(user: AppUser) {
	return user.type !== UserType.Student;
}

function isThesisStaff(user: AppUser) {
	return [UserType.Admin, UserType.ThesesBoardMember].includes(user.type);
}

export function canVote(user: AppUser) {
	return isThesisStaff(user);
}

export function canModifyThesis(user: AppUser, thesis: Thesis) {
	return (
		isThesisStaff(user) ||
		user.type === UserType.Employee &&
		thesis.status !== ThesisStatus.Accepted &&
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
