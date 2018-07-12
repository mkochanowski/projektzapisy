import * as React from "react";
import ReactTable, { Column } from "react-table";
import "react-table/react-table.css";

import { Thesis, Employee } from "../types";

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
	accessor: (props: Thesis) => props.reserved
}, {
	id: "thesisKind",
	Header: "Typ",
	accessor: (props: Thesis) => props.kind,
}, {
	id: "thesisAdvisor",
	Header: "Promotor",
	accessor: (props: Thesis) => formatEmployeeDisplayName(props.advisor)
}, {
	id: "thesisName",
	Header: "Tytuł",
	accessor: (props: Thesis) => props.title
}];

export class ThesesList extends React.Component<Props, State> {
	render(): JSX.Element {
		return <ReactTable
			data={this.props.currentThesesList}
			columns={TABLE_COL_DECLS}
		/>;
	}
}
