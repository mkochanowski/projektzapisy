// Must match values/structures defined in the Python backend

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

// export type StudentRaw = {
//
// };

export type EmployeeRaw = {
	id: number,
	title: string,
	user: {
		id: number,
		username: string,
		first_name: string,
		last_name: string,
	},
};

export class Employee {
	public id: number;
	public academicTitle?: string;
	public userId: number;
	public username: string;
	public firstName: string;
	public lastName: string;

	public constructor(raw: EmployeeRaw) {
		this.id = raw.id;
		if (raw.title) {
			this.academicTitle = raw.title;
		}
		this.userId = raw.user.id;
		this.username = raw.user.username;
		this.firstName = raw.user.first_name;
		this.lastName = raw.user.last_name;
	}

	public getDisplayName(): string {
		const fullName = `${this.firstName} ${this.lastName}`;
		return this.academicTitle ? `${this.academicTitle} ${fullName}` : fullName;
	}
}

export type ThesisRaw = {
	id: number;
	title: string;
	advisor: EmployeeRaw,
	auxiliary_advisor?: EmployeeRaw,
	kind: ThesisKind,
	reserved: boolean,
	description: string,
	status: ThesisStatus,
	added_date: string,
	modified_date: string,
};

export class Thesis {
	public id: number;
	public title: string;
	public advisor: Employee;
	public auxiliaryAdvisor?: Employee;
	public kind: ThesisKind;
	public reserved: boolean;
	public description: string;
	public status: ThesisStatus;
	public addedDate: Date;
	public modifiedDate: Date;

	public constructor(raw: ThesisRaw) {
		this.id = raw.id;
		this.title = raw.title;
		this.advisor = new Employee(raw.advisor);
		if (raw.auxiliary_advisor) {
			this.auxiliaryAdvisor = new Employee(raw.auxiliary_advisor);
		}
		this.kind = raw.kind;
		this.reserved = raw.reserved;
		this.description = raw.description;
		this.status = raw.status;
		this.addedDate = new Date(raw.added_date);
		this.modifiedDate = new Date(raw.modified_date);
	}
}
