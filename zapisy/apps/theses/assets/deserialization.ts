import * as moment from "moment";

import { ThesisKind, ThesisStatus, UserType } from "./protocol_types";
import { Thesis } from "./thesis";
import { Employee, Student, AppUser } from "./users";
import { Users } from "./app_logic/users";

type PersonInJson = {
	id: number;
	name: string;
};

/**
 * This is the format in which we receive theses from the backend
 */
export type ThesisInJson = {
	id: number;
	title: string;
	advisor?: number;
	auxiliary_advisor?: number;
	kind: ThesisKind;
	reserved_until: string | null;
	description: string;
	status: ThesisStatus;
	student?: PersonInJson;
	student_2?: PersonInJson;
	modified_date: string;
};

type CurrentUserInJson = {
	user: PersonInJson;
	type: UserType;
};

export function deserializeEmployee(json: PersonInJson) {
	return new Employee(json.id, json.name);
}

export function deserializeStudent(json: PersonInJson) {
	return new Student(json.id, json.name);
}

export function deserializeThesis(json: ThesisInJson) {
	const result = new Thesis();
	result.id = json.id;
	result.title = json.title;
	result.advisor = json.advisor ? Users.getEmployeeById(json.advisor) : null;
	result.auxiliaryAdvisor = json.auxiliary_advisor ? Users.getEmployeeById(json.auxiliary_advisor) : null;
	result.kind = json.kind;
	result.reservedUntil = json.reserved_until ? moment(json.reserved_until) : null;
	result.description = json.description;
	result.status = json.status;
	result.student = json.student ? deserializeStudent(json.student) : null;
	result.secondStudent = json.student_2 ? deserializeStudent(json.student_2) : null;
	result.modifiedDate = moment(json.modified_date);
	return result;
}

export function deserializeCurrentUser(json: CurrentUserInJson) {
	const deserializer = json.type === UserType.Student
		? deserializeStudent
		: deserializeEmployee;
	return new AppUser(deserializer(json.user), json.type);
}

type BoardMemberIn = number;
export function deserializeBoardMember(member: BoardMemberIn) {
	const result = Users.getEmployeeById(member);
	if (!result) {
		console.error(`Board member with ID ${member} not found, skipping`);
		return null;
	}
	return result;
}
