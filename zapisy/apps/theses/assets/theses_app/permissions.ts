import { AppUser, UserType, Thesis } from "./types";

export function canAddThesis(type: UserType) {
	return type !== UserType.Student;
}

function isThesisStaff(type: UserType) {
	return [UserType.Admin, UserType.ThesesBoardMember].includes(type);
}

export function canVote(type: UserType) {
	return isThesisStaff(type);
}

export function canModifyThesis(user: AppUser, thesis: Thesis) {
	if (isThesisStaff(user.type)) {
		return true;
	}
	return (
		user.type === UserType.Employee &&
		thesis.advisor !== null &&
		thesis.advisor.id === user.id
	);
}
