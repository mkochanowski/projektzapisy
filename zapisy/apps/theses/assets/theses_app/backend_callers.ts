import { Thesis } from "./types";

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
	const resp = await fetch(url);
	if (!resp.ok) {
		throw new Error(`Did not get a successful fetch response: ${resp.status} ${resp.statusText}`);
	}
	return resp.json();
}

export function getThesesList(filterType: ThesisTypeFilter): Promise<Thesis[]> {
	return fetchJson(`${BASE_API_URL}/theses?thesis_type=${filterType}`);
}
