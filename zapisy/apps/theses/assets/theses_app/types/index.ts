// Must match values/structures defined in the Python backend
import * as moment from "moment";

export const MAX_THESIS_TITLE_LEN = 300;

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

export function thesisStatusToString(status: ThesisStatus) {
	switch (status) {
		case ThesisStatus.Accepted: return "Zaakceptowana";
		case ThesisStatus.BeingEvaluated: return "Poddana pod głosowanie";
		case ThesisStatus.Defended: return "Obroniona";
		case ThesisStatus.InProgress: return "W realizacji";
		case ThesisStatus.ReturnedForCorrections: return "Zwrócona do poprawek";
	}
}

export const enum ThesisVote {
	None = 1,
	Rejected = 2,
	Accepted = 3,
	UserMissing = 4,
}

export type PersonJson = {
	id: number;
	display_name: string;
};

export class BasePerson {
	public id: number;
	public displayName: string;

	public constructor(id: number, displayName: string) {
		this.id = id;
		this.displayName = displayName;
	}

	public static fromJson(raw: PersonJson) {
		return new BasePerson(raw.id, raw.display_name);
	}

	public isEqual = (other: BasePerson): boolean => {
		return this.id === other.id;
	}
}

export class Employee extends BasePerson {}
export class Student extends BasePerson {}

export type ThesisJson = {
	id: number;
	title: string;
	advisor?: PersonJson;
	auxiliary_advisor?: PersonJson;
	kind: ThesisKind;
	reserved: boolean;
	description: string;
	status: ThesisStatus;
	student?: PersonJson;
	student_2?: PersonJson;
	added_date: string;
	modified_date: string;
	votes: { [id: number]: ThesisVote };
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
	public votes: { [id: number]: ThesisVote };

	public constructor(json?: ThesisJson) {
		if (json) {
			this.initFromJson(json);
		} else {
			this.initNewThesis();
		}
	}

	private initFromJson(json: ThesisJson) {
		this.id = json.id;
		this.title = json.title;
		this.advisor = json.advisor ? Employee.fromJson(json.advisor) : null;
		this.auxiliaryAdvisor = json.auxiliary_advisor ? Employee.fromJson(json.auxiliary_advisor) : null;
		this.kind = json.kind;
		this.reserved = json.reserved;
		this.description = json.description;
		this.status = json.status;
		this.student = json.student ? Employee.fromJson(json.student) : null;
		this.secondStudent = json.student_2 ? Employee.fromJson(json.student_2) : null;
		this.addedDate = moment(json.added_date);
		this.modifiedDate = moment(json.modified_date);
		this.votes = json.votes;
	}

	private initNewThesis() {
		this.id = -1;
		this.title = "";
		this.advisor = null;
		this.auxiliaryAdvisor = null;
		this.kind = ThesisKind.Bachelors;
		this.reserved = false;
		this.description = "";
		this.status = ThesisStatus.BeingEvaluated;
		this.student = null;
		this.secondStudent = null;
		this.addedDate = moment();
		this.modifiedDate = moment();
		this.votes = {};
	}

	public isEqual = (other: Thesis): boolean => {
		return this.id === other.id;
	}

	public areValuesEqual(other: Thesis): boolean {
		console.assert(
			this.isEqual(other),
			"Thesis::areValuesEqual only makes sense for two theses with the same ID",
		);
		return (
			this.title === other.title &&
			this.description === other.description &&
			this.personValuesEqual(this.advisor, other.advisor) &&
			this.personValuesEqual(this.auxiliaryAdvisor, other.auxiliaryAdvisor) &&
			this.personValuesEqual(this.student, other.student) &&
			this.personValuesEqual(this.secondStudent, other.secondStudent) &&
			this.kind === other.kind &&
			this.reserved === other.reserved &&
			this.status === other.status &&
			this.modifiedDate.isSame(other.modifiedDate)
		);
	}

	private personValuesEqual(p1: BasePerson | null, p2: BasePerson | null): boolean {
		return (
			p1 === null && p2 === null ||
			p1 !== null && p2 !== null && p1.isEqual(p2)
		);
	}
}

export const enum UserType {
	Student,
	Employee,
	ThesesBoardMember,
	Admin,
}

type CurrentUserJson = {
	user: PersonJson;
	type: UserType;
};

export class AppUser {
	public user: BasePerson;
	public type: UserType;

	public constructor(json: CurrentUserJson) {
		this.user = BasePerson.fromJson(json.user);
		this.type = json.type;
	}
}
