/*
	Logic related to sorting/filtering theses based
	on user settings in the UI
*/

import { Thesis, ThesisStatus, ThesisKind, BasePerson, ThesisTypeFilter } from "../types";
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

// Whenever the sorting or filters change, getProcessedTheses will be called
// anew with the parameters specified. However, if we only change the sorting,
// we don't really want to pay the cost of filtering the list as this can
// be relatively expensive (substring checks on every instance), so we cache the results
// based on the parameters specified - see filterData.
// Of course, if a new theses list is fetched from the backend the cache must be invalidated;
// clearFilterCache below does this.
const filterCache: Map<string, Thesis[]> = new Map();

// The results returned by this module are determined by these parameters
export type ThesesProcessParams = {
	advisor: string;
	title: string;
	type: ThesisTypeFilter;

	sortColumn: SortColumn;
	sortDirection: SortDirection;
};

/**
 * Process the given theses list using the given parameters.
 *
 * @param theses - The raw theses list to be processed
 * @param params - The parameters to use for the processing
 */
export function getProcessedTheses(theses: Thesis[], params: ThesesProcessParams): Thesis[] {
	const filteredData = filterData(theses, params.advisor, params.title, params.type);
	return sortData(filteredData, params.sortColumn, params.sortDirection);
}

/**
 * Clear the filter results cache. Needs to be called whenver the raw theses list changes.
 */
export function clearFilterCache() {
	filterCache.clear();
}

function filterData(data: Thesis[], advisor: string, title: string, type: ThesisTypeFilter) {
	advisor = advisor.toLowerCase();
	title = title.toLowerCase();

	const cacheKey = `${advisor}_${title}_${type}`;
	const cached = filterCache.get(cacheKey);
	if (cached) {
		return cached;
	}

	const r = data.filter(thesis => (
		thesisMatchesType(thesis, type) &&
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

/**
 * Determine whether the specified person matches the specified name filter
 */
function personNameFilter(p: BasePerson | null, nameFilt: string): boolean {
	return p === null || p.displayName.toLowerCase().includes(nameFilt);
}

/**
 * Determine whether the specified thesis should be considered as "available"
 */
function isThesisAvailable(thesis: Thesis): boolean {
	return (
		thesis.status !== ThesisStatus.InProgress &&
		thesis.status !== ThesisStatus.Defended &&
		!thesis.reserved
	);
}

/**
 * Determine whether the specified thesis matches the specified type
 */
function thesisMatchesType(thesis: Thesis, type: ThesisTypeFilter) {
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
	}
}
