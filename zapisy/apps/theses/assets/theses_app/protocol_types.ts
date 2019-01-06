/**
 * @file Defines misc types used when interacting with the backend;
 * this should be kept synchronized with types defined there
 */

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

export const enum ThesisVote {
	None = 1,
	Rejected = 2,
	Accepted = 3,
}

/**
 * Defines the type of user using the thesis system
 */
export const enum UserType {
	Student,
	Employee,
	Admin,
}

/** Defines the filter values sent to the backend when retrieving theses */
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
