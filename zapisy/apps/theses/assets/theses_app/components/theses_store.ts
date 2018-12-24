import { ThesisTypeFilter } from "../backend_callers";
import { Thesis, ThesisStatus, ThesisKind, BasePerson, AppUser, UserType, ThesisVote } from "../types";
import { strcmp } from "common/utils";

export const enum SortDirection {
	Asc,
	Desc,
}

export const enum SortColumn {
	None,
	Advisor,
	Title,
}

const filterCache: Map<string, Thesis[]> = new Map();

export type ThesesProcessParams = {
	advisor: string;
	title: string;
	type: ThesisTypeFilter;

	sortColumn: SortColumn;
	sortDirection: SortDirection;
};

export function getProcessedTheses(
	theses: Thesis[], params: ThesesProcessParams, user: AppUser,
): Thesis[] {
	const filteredData = filterData(theses, params.advisor, params.title, params.type, user);
	return sortData(filteredData, params.sortColumn, params.sortDirection);
}

export function clearFilterCache() {
	filterCache.clear();
}

function filterData(
	data: Thesis[], advisor: string, title: string, type: ThesisTypeFilter,
	user: AppUser,
) {
	advisor = advisor.toLowerCase();
	title = title.toLowerCase();

	const cacheKey = `${advisor}_${title}_${type}`;
	const cached = filterCache.get(cacheKey);
	if (cached) {
		return cached;
	}

	const r = data.filter(thesis => (
		thesisMatchesType(thesis, type, user) &&
		personNameFilter(thesis.advisor, advisor) &&
		thesis.title.toLowerCase().includes(title)
	));
	filterCache.set(cacheKey, r);
	return r;
}

function sortData(data: Thesis[], sortColumn: SortColumn, sortDirection: SortDirection): Thesis[] {
	if (sortColumn === SortColumn.None) {
		return data;
	}
	const getter = (
		sortColumn === SortColumn.Advisor
		? (t: Thesis) => t.advisor != null ? t.advisor.displayName : ""
		: (t: Thesis) => t.title
	);
	const applyDir = sortDirection === SortDirection.Asc
		? (r: number) => r : (r: number) => -r;

	return data.slice().sort((t1: Thesis, t2: Thesis) => (
		applyDir(strcmp(getter(t1), getter(t2)))
	));
}

function personNameFilter(p: BasePerson | null, nameFilt: string): boolean {
	return p === null || p.displayName.toLowerCase().includes(nameFilt);
}

function isThesisAvailable(thesis: Thesis): boolean {
	return (
		thesis.status !== ThesisStatus.InProgress &&
		thesis.status !== ThesisStatus.Defended &&
		!thesis.reserved
	);
}

function thesisMatchesType(thesis: Thesis, type: ThesisTypeFilter, user: AppUser) {
	switch (type) {
		case ThesisTypeFilter.All: return true;
		case ThesisTypeFilter.AllCurrent: return isThesisAvailable(thesis);
		case ThesisTypeFilter.Masters: return thesis.kind === ThesisKind.Masters;
		case ThesisTypeFilter.Engineers: return thesis.kind === ThesisKind.Engineers;
		case ThesisTypeFilter.Bachelors: return thesis.kind === ThesisKind.Bachelors;
		case ThesisTypeFilter.BachelorsISIM: return thesis.kind === ThesisKind.Isim;
		case ThesisTypeFilter.AvailableMasters:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Masters;
		case ThesisTypeFilter.AvailableEngineers:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Engineers;
		case ThesisTypeFilter.AvailableBachelors:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Bachelors;
		case ThesisTypeFilter.AvailableBachelorsISIM:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Isim;
		case ThesisTypeFilter.Ungraded:
			console.assert(user.type === UserType.ThesesBoardMember);
			return thesis.getMemberVote(user.user) === ThesisVote.None;
	}
}
