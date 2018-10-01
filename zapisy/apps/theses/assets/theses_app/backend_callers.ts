import { get as getCookie } from "js-cookie";
import * as objectAssignDeep from "object-assign-deep";
import axios, { AxiosRequestConfig } from "axios";

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

async function sendRequestWithCsrf(url: string, config?: AxiosRequestConfig) {
	const tokenValue = getCookie("csrftoken");
	if (!tokenValue) {
		throw new Error("CSRF token not found in cookies");
	}

	return axios.request(
		objectAssignDeep({}, config, {
			url,
			headers: { "X-CSRFToken": tokenValue }
		})
	);
}

async function getData(url: string, config?: AxiosRequestConfig): Promise<any> {
	return (await axios.get(url, config)).data;
}

export async function getThesesList(
	filterType: ThesisTypeFilter, title: string, advisorName: string,
): Promise<Thesis[]> {
	const results: ThesisJson[] = await getData(
		`${BASE_API_URL}/theses`,
		{ params: {
			type: filterType,
			title,
			advisor: advisorName,
		}},
	);
	return results.map(json => new Thesis(json));
}

export async function getThesisById(id: number): Promise<Thesis> {
	const json: ThesisJson = await getData(`${BASE_API_URL}/theses/${id}`);
	return new Thesis(json);
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
	const url = `/theses/${personUrlPart}-autocomplete`;
	const acResults = await getData(url, { params: {
		page: pageNum,
		q: substr,
	}}) as PersonAutocompleteJson;
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
	await sendRequestWithCsrf(
		`${BASE_API_URL}/theses/${diffObj.id}/`,
		{
			method: "PATCH",
			data: jsonData,
			headers: {
				"Content-Type": "application/json"
			},
		},
	);
}
