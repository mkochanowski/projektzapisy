import * as React from "react";
import { ThesisTypeFilter } from "../../backend_callers";
import { GenericSelect } from "../GenericSelect";

const filterInfos = [
	{ val: ThesisTypeFilter.AllCurrent, displayName: "Wszystkie aktualne" },
	{ val: ThesisTypeFilter.All, displayName: "Wszystkie" },
	{ val: ThesisTypeFilter.Masters, displayName: "Magisterskie" },
	{ val: ThesisTypeFilter.Engineers, displayName: "Inżynierskie" },
	{ val: ThesisTypeFilter.Bachelors, displayName: "Licencjackie" },
	{ val: ThesisTypeFilter.BachelorsISIM, displayName: "Licencjackie ISIM" },
	{ val: ThesisTypeFilter.AvailableMasters, displayName: "Magisterskie - dostępne" },
	{ val: ThesisTypeFilter.AvailableEngineers, displayName: "Inżynierskie - dostępne" },
	{ val: ThesisTypeFilter.AvailableBachelors, displayName: "Licencjackie - dostępne" },
	{ val: ThesisTypeFilter.AvailableBachelorsISIM, displayName: "Licencjackie ISIM - dostępne" },
];

type Props = {
	onChange: (newFilter: ThesisTypeFilter) => void;
	value: ThesisTypeFilter;
};

export function ThesesFilter(props: Props) {
	const selectComponentClass = GenericSelect<ThesisTypeFilter>(
		"Rodzaj", filterInfos, { fontWeight: "bold", fontSize: "110%" },
	);
	return new selectComponentClass(props);
}
