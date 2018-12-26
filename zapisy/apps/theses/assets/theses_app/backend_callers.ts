/**
 * @file Contains functions that permit interaction
 * with the backend - both pure getters and modifiers
 */
import { get as getCookie } from "js-cookie";
import * as objectAssignDeep from "object-assign-deep";
import axios, { AxiosRequestConfig } from "axios";

import {
	Thesis, ThesisJson, Student, Employee,
	BasePerson, AppUser, ThesisTypeFilter,
} from "./types";
import { getThesisModDispatch, getThesisAddDispatch } from "./types/dispatch";

const BASE_API_URL = "/theses/api";
const REST_REQUEST_TIMEOUT = 10000;

axios.defaults.timeout = REST_REQUEST_TIMEOUT;

/**
 * Send a request to the backend including the csrf token
 * supplied by Django's auth system; all requests
 * should go through this function because otherwise they will be rejected
 * as unauthorized
 * @param url The URL
 * @param config Optional Axios request config
 */
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

/**
 * Perform a request, then return the body of the response
 * @param url The URL
 * @param config Optional Axios request config
 */
async function getData(url: string, config?: AxiosRequestConfig): Promise<any> {
	return (await axios.get(url, config)).data;
}

export const enum SortDirection {
	Asc,
	Desc,
}

export const enum SortColumn {
	None,
	Advisor,
	Title,
}

/**
 * Thesis processing parameters; the results of getProcessedTheses depend on this
 */
export type ThesesProcessParams = {
	advisor: string;
	title: string;
	type: ThesisTypeFilter;

	sortColumn: SortColumn;
	sortDirection: SortDirection;
};

type PaginatedThesesResult = {
	count: number;
	next: string;
	previous: string;
	results: ThesisJson[];
};

function sortColToBackendStr(col: SortColumn) {
	switch (col) {
		case SortColumn.Advisor: return "advisor";
		case SortColumn.Title: return "title";
		case SortColumn.None: return "";
	}
}

function sortDirToBackendStr(dir: SortDirection) {
	switch (dir) {
		case SortDirection.Asc: return "asc";
		case SortDirection.Desc: return "desc";
	}
}

export async function getThesesList(params: ThesesProcessParams, page: number) {
	const paginatedResults: PaginatedThesesResult = await getData(
		`${BASE_API_URL}/theses`,
		{ params: {
			type: params.type,
			title: params.title,
			advisor: params.advisor,
			column: sortColToBackendStr(params.sortColumn),
			dir: sortDirToBackendStr(params.sortDirection),
			page: page,
		}},
	);
	return {
		theses: paginatedResults.results.map(json => new Thesis(json)),
		total: paginatedResults.count,
	};
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
/**
 * Use django-autocomplete-light's endpoint (also used by thesis forms in Django admin)
 * to fetch all matching students/employees
 * @param person The person type - determines which endpoint to use
 * @param substr The name filter - only persons matching this will be returned
 * @param pageNum Which page to return
 */
export async function getPersonAutocomplete(
	person: PersonType, substr: string, pageNum: number,
): Promise<PersonAutcompleteResults> {
	const personUrlPart = person === PersonType.Employee ? "employee" : "student";
	const url = `${BASE_API_URL}/${personUrlPart}-autocomplete`;
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

/**
 * Given a previous and a modified thesis instance, compute the diff
 * and dispatch a request to the backend
 * @param originalThesis The old thesis object
 * @param modifiedThesis The new (modified) thesis object
 */
export async function saveModifiedThesis(
	originalThesis: Thesis, modifiedThesis: Thesis,
): Promise<void> {
	const objToSend = getThesisModDispatch(originalThesis, modifiedThesis);
	const jsonData = JSON.stringify(objToSend);
	console.warn("Sending", jsonData);
	await sendRequestWithCsrf(
		`${BASE_API_URL}/theses/${objToSend.id}/`,
		{
			method: "PATCH",
			data: jsonData,
			headers: {
				"Content-Type": "application/json"
			},
		},
	);
}

/**
 * Given a thesis object, serialize it and dispatch a request
 * to add it to the backend
 * @param thesis The thesis object to add
 */
export async function saveNewThesis(thesis: Thesis): Promise<number> {
	const objToSend = getThesisAddDispatch(thesis);
	const jsonData = JSON.stringify(objToSend);
	console.warn("Adding:", jsonData);
	const res = await sendRequestWithCsrf(
		`${BASE_API_URL}/theses/`,
		{
			method: "POST",
			data: jsonData,
			headers: {
				"Content-Type": "application/json"
			},
		},
	);
	return (res.data as ThesisJson).id;
}

/**
 * Fetch the current system user from the backend
 */
export async function getCurrentUser(): Promise<AppUser> {
	return new AppUser(await getData(`${BASE_API_URL}/current_user`));
}
