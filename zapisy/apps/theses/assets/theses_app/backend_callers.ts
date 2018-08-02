import { stringify } from "query-string";
import { get as getCookie } from "js-cookie";
import * as objectAssignDeep from "object-assign-deep";

import { Thesis, ThesisJson, Student, Employee, BasePerson } from "./types";
import { getOutThesisJson } from "./types/out";

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

async function sendFetchRequest(url: string, options?: RequestInit): Promise<Response> {
	console.warn(objectAssignDeep);
	const finalOptions = objectAssignDeep({ credentials: "include" }, options);
	console.warn("Dispatching a request to", url, "with options", finalOptions);
	const resp = await fetch(url, finalOptions);
	if (!resp.ok) {
		throw new Error(`Did not get a successful fetch response: ${resp.status} ${resp.statusText}`);
	}
	return resp;
}

async function sendFetchRequestWithCsrf(url: string, options?: RequestInit): Promise<Response> {
	const tokenValue = getCookie("csrftoken");
	if (!tokenValue) {
		throw new Error("CSRF token not found in cookies");
	}
	return sendFetchRequest(
		url,
		objectAssignDeep({}, options, {
			headers: { "X-CSRFToken": tokenValue }
		})
	);
}

async function fetchJson(url: string): Promise<any> {
	return (await sendFetchRequest(url)).json();
}

export async function getThesesList(filterType: ThesisTypeFilter): Promise<Thesis[]> {
	const results: ThesisJson[] = await fetchJson(`${BASE_API_URL}/theses?thesis_type=${filterType}`);
	return results.map(json => new Thesis(json));
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
			raw => new constr(raw.id, raw.text)
		),
		hasMore: acResults.pagination.more,
	};
}

export async function saveModifiedThesis(originalThesis: Thesis, modifiedThesis: Thesis): Promise<void> {
	const diffObj = getOutThesisJson(originalThesis, modifiedThesis);
	const jsonData = JSON.stringify(diffObj);
	console.warn("Sending", jsonData);
	await sendFetchRequestWithCsrf(
		`${BASE_API_URL}/theses/${diffObj.id}/`,
		{
			method: "PATCH",
			body: jsonData,
			headers: {
				"Content-Type": "application/json"
			},
		},
	);
}
