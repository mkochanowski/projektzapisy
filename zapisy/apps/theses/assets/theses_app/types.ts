// Must match values/structures defined in the Python backend
import * as moment from "moment";

export const enum ThesisKind {
	Masters = 0,
	Engineers = 1,
	Bachelors = 2,
	BachelorsEngineers = 3,
	Isim = 4,
}

export function thesisKindToString(kind: ThesisKind): string {
	switch (kind) {
		case ThesisKind.Masters: return "mgr";
		case ThesisKind.Engineers: return "inż";
		case ThesisKind.Bachelors: return "lic";
		case ThesisKind.BachelorsEngineers: return "lic+inż";
		case ThesisKind.Isim: return "ISIM";
	}
}

export const enum ThesisStatus {
	BeingEvaluated = 1,
	ReturnedForCorrections = 2,
	Accepted = 3,
	InProgress = 4,
	Defended = 5,
}

export const enum ThesisVote {
	None = 1,
	Rejected = 2,
	Accepted = 3,
	UserMissing = 4,
}

type PersonRaw = {
	id: number;
	display_name: string;
};

export class BasePerson {
	public id: number;
	public displayName: string;

	public constructor(raw: PersonRaw) {
		this.id = raw.id;
		this.displayName = raw.display_name;
	}
}

export class Employee extends BasePerson {}
export class Student extends BasePerson {}

export type ThesisRaw = {
	id: number;
	title: string;
	advisor?: PersonRaw;
	auxiliary_advisor?: PersonRaw;
	kind: ThesisKind;
	reserved: boolean;
	description: string;
	status: ThesisStatus;
	student?: PersonRaw;
	student_2?: PersonRaw;
	added_date: string;
	modified_date: string;
};

export class Thesis {
	public id: number;
	public title: string;
	public advisor: Employee | null;
	public auxiliaryAdvisor: Employee | null;
	public kind: ThesisKind;
	public reserved: boolean;
	public description: string;
	public status: ThesisStatus;
	public student: Student | null;
	public secondStudent: Student | null;
	public addedDate: moment.Moment;
	public modifiedDate: moment.Moment;

	public constructor(raw: ThesisRaw) {
		this.id = raw.id;
		this.title = raw.title;
		this.advisor = raw.advisor ? new Employee(raw.advisor) : null;
		this.auxiliaryAdvisor = raw.auxiliary_advisor ? new Employee(raw.auxiliary_advisor) : null;
		this.kind = raw.kind;
		this.reserved = raw.reserved;
		this.description = raw.description;
		this.status = raw.status;
		this.student = raw.student ? new Student(raw.student) : null;
		this.secondStudent = raw.student_2 ? new Student(raw.student_2) : null;
		this.addedDate = moment(raw.added_date);
		this.modifiedDate = moment(raw.modified_date);
	}
}
