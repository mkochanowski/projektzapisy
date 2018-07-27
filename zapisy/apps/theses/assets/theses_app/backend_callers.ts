import { stringify } from "query-string";

import { Thesis, ThesisRaw, Student, Employee, BasePerson } from "./types";

const BASE_API_URL = "/theses/api";

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

async function fetchJson(url: string): Promise<any> {
	const resp = await fetch(url, { credentials: "include" });
	if (!resp.ok) {
		throw new Error(`Did not get a successful fetch response: ${resp.status} ${resp.statusText}`);
	}
	return resp.json();
}

export async function getThesesList(filterType: ThesisTypeFilter): Promise<Thesis[]> {
	const results: ThesisRaw[] = await fetchJson(`${BASE_API_URL}/theses?thesis_type=${filterType}`);
	return results.map(raw => new Thesis(raw));
}

export const enum PersonType {
	Employee,
	Student,
}

export type PersonAutcompleteResults = {
	results: BasePerson[];
	hasMore: boolean;
};
type PersonAutocompleteJson = {
	pagination: {
		more: boolean;
	};
	results: Array<{
		id: number;
		text: string;
	}>;
};
export async function getPersonAutocomplete(
	person: PersonType, substr: string, pageNum: number,
): Promise<PersonAutcompleteResults> {
	const personUrlPart = person === PersonType.Employee ? "employee" : "student";
	const queryString = stringify({
		page: pageNum,
		q: substr,
	});
	const url = `/theses/${personUrlPart}-autocomplete?${queryString}`;
	const acResults = await fetchJson(url) as PersonAutocompleteJson;
	const constr = person === PersonType.Employee ? Employee : Student;
	return {
		results: acResults.results.map(
			raw => new constr({ id: raw.id, display_name: raw.text })
		),
		hasMore: acResults.pagination.more,
	};
}
