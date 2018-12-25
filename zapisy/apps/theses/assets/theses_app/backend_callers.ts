/*
	This file contains functions that permit interaction
	with the backend - both pure getters and modifiers
*/

import { get as getCookie } from "js-cookie";
import * as objectAssignDeep from "object-assign-deep";
import axios, { AxiosRequestConfig } from "axios";

import { Thesis, ThesisJson, Student, Employee, BasePerson, AppUser } from "./types";
import { getThesisModDispatch, getThesisAddDispatch } from "./types/dispatch";

const BASE_API_URL = "/theses/api";
const REST_REQUEST_TIMEOUT = 10000;

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

axios.defaults.timeout = REST_REQUEST_TIMEOUT;

// Send a request to the backend including the csrf token
// supplied by Django's auth system; all requests
// should go through this function because otherwise they will be rejected
// as unauthorized
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

// Perform a request, then return the body of the response
async function getData(url: string, config?: AxiosRequestConfig): Promise<any> {
	return (await axios.get(url, config)).data;
}

// Fetch the list of all theses from the backend, return an array
// of local Thesis class instances
export async function getThesesList(
) {
	const rawData: ThesisJson[] = await getData(`${BASE_API_URL}/theses`);
	return rawData.map(json => new Thesis(json));
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
// Use django-autocomplete-light's endpoint (also used by thesis forms in Django admin)
// to fetch all matching students/employees
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

// Given a previous and a modified thesis instance, compute the diff
// and dispatch a request to the backend
export async function saveModifiedThesis(originalThesis: Thesis, modifiedThesis: Thesis): Promise<void> {
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

// Given a thesis object, serialize it and dispatch a request
// to add it to the backend
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

// Fetch the current system user from the backend
export async function getCurrentUser(): Promise<AppUser> {
	return new AppUser(await getData(`${BASE_API_URL}/current_user`));
}
