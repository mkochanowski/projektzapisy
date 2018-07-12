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

export type Thesis = {
	id: number;
	title: string;
	advisor: {
		id: number,
		user: {
			id: number,
			username: string,
			first_name: string,
			last_name: string,
		},
	},
	kind: ThesisKind,
};
