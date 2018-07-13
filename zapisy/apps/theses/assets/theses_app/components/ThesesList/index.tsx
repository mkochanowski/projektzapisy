import * as React from "react";
import ReactTable, { Column, RowInfo } from "react-table";
import "react-table/react-table.css";

import { Thesis, Employee } from "../../types";
import { ReservationIndicator } from "./ReservationIndicator";

type Props = {
	currentThesesList: Thesis[],
};

type State = {
	searchPhrase: string,
};

function formatEmployeeDisplayName(employee: Employee): string {
	const fullName = `${employee.user.first_name} ${employee.user.last_name}`;
	return employee.title ? `${employee.title} ${fullName}` : fullName;
}

const TABLE_COL_DECLS: Column[] = [{
	id: "isThesisReserved",
	Header: "Rezerwacja",
	accessor: (props: Thesis) => props.reserved,
	Cell: props => <ReservationIndicator reserved={props.value} />,
	width: 100,
}, {
	id: "thesisKind",
	Header: "Typ",
	accessor: (props: Thesis) => props.kind,
	filterable: true,
	width: 80,
}, {
	id: "thesisAdvisor",
	Header: "Promotor",
	accessor: (props: Thesis) => formatEmployeeDisplayName(props.advisor),
	filterable: true,
}, {
	id: "thesisName",
	Header: "Tytuł",
	accessor: (props: Thesis) => props.title,
	filterable: true,
}];

function getTableProps() {
	return { style: { textAlign: "center" } };
}

function getTheadProps() {
	return { style: {
		fontWeight: "bold",
		fontSize: "120%",
	}};
}

function getTrProps(_: any, rowInfo: RowInfo | undefined) {
	if (rowInfo) {
		// console.warn(rowInfo);
		return { style: {
			background: rowInfo.viewIndex % 2 ? "#e8e8e8" : "white",
		}};
	}
	return {};
}

export class ThesesList extends React.Component<Props, State> {
	render(): JSX.Element {
		return <ReactTable
			data={this.props.currentThesesList}
			columns={TABLE_COL_DECLS}
			defaultPageSize={10}
			getTableProps={getTableProps}
			getTheadProps={getTheadProps}
			getTrProps={getTrProps}
			style={{
				height: "400px"
			}}
		/>;
	}
}
