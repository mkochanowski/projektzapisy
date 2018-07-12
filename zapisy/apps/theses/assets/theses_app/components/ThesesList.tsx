import * as React from "react";
import ReactTable, { Column } from "react-table";
import "react-table/react-table.css";

import { Thesis } from "../types";

type Props = {
	currentThesesList: Thesis[],
};

type State = {
	searchPhrase: string,
};

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
	accessor: (props: Thesis) => props.advisor.user.first_name + props.advisor.user.last_name
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
