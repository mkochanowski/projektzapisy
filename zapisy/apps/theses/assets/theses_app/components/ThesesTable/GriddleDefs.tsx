import { ColumnMetaData } from "griddle-react";

import { ReservationIndicator } from "../ReservationIndicator";

export const griddleColumnMeta: Array<ColumnMetaData<any>> = [
	{
		columnName: "reserved",
		displayName: "Rezerwacja",
		customComponent: ReservationIndicator,
		cssClassName: "reservedColumn",
		sortable: false,
	},
	{
		columnName: "title",
		displayName: "Tytuł",
		cssClassName: "titleColumn",
	},
	{
		columnName: "advisorName",
		displayName: "Promotor",
		cssClassName: "advisorColumn",
	},
];

export const THESES_PER_PAGE = 10;
export const GRIDDLE_NO_DATA = "Brak wyników";
export const GRIDDLE_TABLE_HEIGHT = 200;

// Converted theses data passed to griddle for rendering
export type GriddleThesisData = {
	id: number;
	idx: number;
	reserved: boolean;
	title: string;
	advisorName: string;
};
