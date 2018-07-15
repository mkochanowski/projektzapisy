// Must match values/structures defined in the Python backend

export const enum ThesisKind {
	Masters = 0,
	Engineers = 1,
	Bachelors = 2,
	BachelorsEngineers = 3,
	Isim = 4,
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

export type Employee = {
	id: number,
	title: string,
	user: {
		id: number,
		username: string,
		first_name: string,
		last_name: string,
	},
};

export type ThesisRaw = {
	id: number;
	title: string;
	advisor: Employee,
	auxiliary_advisor?: Employee,
	kind: ThesisKind,
	reserved: boolean,
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
	public status: ThesisStatus;
	public addedDate: Date;
	public modifiedDate: Date;

	public constructor(raw: ThesisRaw) {
		this.id = raw.id;
		this.title = raw.title;
		this.advisor = raw.advisor;
		if (raw.auxiliary_advisor) {
			this.auxiliaryAdvisor = raw.auxiliary_advisor;
		}
		this.kind = raw.kind;
		this.reserved = raw.reserved;
		this.status = raw.status;
		this.addedDate = new Date(raw.added_date);
		this.modifiedDate = new Date(raw.modified_date);
	}
}
