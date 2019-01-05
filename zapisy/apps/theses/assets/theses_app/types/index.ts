/**
 * @file Defines core types used in the front end code.
 * If you change any of those types, you should most likely also change
 * the Python equivalent in models.py
 */
import * as moment from "moment";

export const MAX_THESIS_TITLE_LEN = 300;

export const enum ThesisKind {
	Masters = 0,
	Engineers = 1,
	Bachelors = 2,
	BachelorsEngineers = 3,
	Isim = 4,
}

/**
 * Stringify a thesis kind
 * @param kind The kind to stringify
 */
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

/**
 * Stringify a thesis status
 * @param status The status to stringify
 */
export function thesisStatusToString(status: ThesisStatus) {
	switch (status) {
		case ThesisStatus.Accepted: return "Zaakceptowana";
		case ThesisStatus.BeingEvaluated: return "Poddana pod głosowanie";
		case ThesisStatus.Defended: return "Obroniona";
		case ThesisStatus.InProgress: return "W realizacji";
		case ThesisStatus.ReturnedForCorrections: return "Zwrócona do poprawek";
	}
}

export const enum ThesisTypeFilter {
	AllCurrent,
	All,
	Masters,
	Engineers,
	Bachelors,
	BachelorsISIM,
	AvailableMasters,
	AvailableEngineers,
	AvailableBachelors,
	AvailableBachelorsISIM,

	Default = AllCurrent,
}

/**
 * Stringify a thesis type filter
 * @param type The type filter to stringify
 */
export function thesisTypeFilterToString(type: ThesisTypeFilter) {
	switch (type) {
		case ThesisTypeFilter.AllCurrent: return "Wszystkie aktualne";
		case ThesisTypeFilter.All: return "Wszystkie";
		case ThesisTypeFilter.Masters: return "Magisterskie";
		case ThesisTypeFilter.Engineers: return "Inżynierskie";
		case ThesisTypeFilter.Bachelors: return "Licencjackie";
		case ThesisTypeFilter.BachelorsISIM: return "Licencjackie ISIM";
		case ThesisTypeFilter.AvailableMasters: return "Magisterskie - dostępne";
		case ThesisTypeFilter.AvailableEngineers: return "Inżynierskie - dostępne";
		case ThesisTypeFilter.AvailableBachelors: return "Licencjackie - dostępne";
		case ThesisTypeFilter.AvailableBachelorsISIM: return "Licencjackie ISIM - dostępne";
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

/**
 * Represents a person in the thesis system
 */
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

/**
 * Represents a university employee in the thesis system
 */
export class Employee extends BasePerson {}
/**
 * Represents a student in the thesis system
 */
export class Student extends BasePerson {}

/**
 * This is the format in which we receive theses from the backend
 */
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
};

/**
 * Native representation of a thesis
 */
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

	/**
	 * Construct a thesis object from JSON if present,
	 * or initialize with defaults otherwise
	 * @param json The optional JSON object from to initialize
	 */
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
	}

	/**
	 * Determine whether this thesis is archived, i.e. has been defended
	 */
	public isArchived() {
		return this.status === ThesisStatus.Defended;
	}

	/**
	 * Is this the same thesis as the supplied one?
	 * @param other The other thesis
	 * Note that because this is a fat arrow it can be conveniently used
	 * as a callback, i.e. theses.find(t.isEqual)
	 */
	public isEqual = (other: Thesis): boolean => {
		return this.id === other.id;
	}

	/**
	 * Determine whether the other instance of the same thesis has been modified;
	 * to compare two possibly different thesis objects, see isEqual above
	 * @param other The other thesis
	 */
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
	Admin,
}

type CurrentUserJson = {
	user: PersonJson;
	type: UserType;
};

/**
 * Represents the user of the thesis system
 */
export class AppUser {
	public user: BasePerson;
	public type: UserType;

	public constructor(json: CurrentUserJson) {
		this.user = BasePerson.fromJson(json.user);
		this.type = json.type;
	}
}
