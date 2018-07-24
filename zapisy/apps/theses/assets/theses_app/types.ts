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

type BasePersonRaw = {
	id: number;
	username: string,
	first_name: string,
	last_name: string,
};

type StudentRaw = BasePersonRaw;
type EmployeeRaw = {
	academic_title: string;
} & BasePersonRaw;

export class BasePerson {
	public id: number;
	public username: string;
	public firstName: string;
	public lastName: string;

	public constructor(raw: BasePersonRaw) {
		this.id = raw.id;
		this.username = raw.username;
		this.firstName = raw.first_name;
		this.lastName = raw.last_name;
	}

	public getDisplayName(): string {
		return `${this.firstName} ${this.lastName}`;
	}
}

export class Employee extends BasePerson {
	public academicTitle?: string;

	public constructor(raw: EmployeeRaw) {
		super(raw);
		if (raw.academic_title) {
			this.academicTitle = raw.academic_title;
		}
	}

	public getDisplayName(): string {
		const fullName = super.getDisplayName();
		return this.academicTitle ? `${this.academicTitle} ${fullName}` : fullName;
	}
}

export class Student extends BasePerson {}

export type ThesisRaw = {
	id: number;
	title: string;
	advisor: EmployeeRaw;
	auxiliary_advisor?: EmployeeRaw;
	kind: ThesisKind;
	reserved: boolean;
	description: string;
	status: ThesisStatus;
	student: StudentRaw;
	student_2?: StudentRaw;
	added_date: string;
	modified_date: string;
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
	public student: Student;
	public secondStudent?: Student;
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
		this.student = new Student(raw.student);
		if (raw.student_2) {
			this.secondStudent = new Student(raw.student_2);
		}
		this.addedDate = new Date(raw.added_date);
		this.modifiedDate = new Date(raw.modified_date);
	}
}
