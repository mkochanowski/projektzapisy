import * as React from "react";
import ReactTable, { Column, RowInfo } from "react-table";
import "react-table/react-table.css";

import { Thesis, Employee, ThesisKind } from "../../types";
import { ReservationIndicator } from "./ReservationIndicator";
import { SearchBox } from "./SearchBox";
import { ThesesFilter } from "./ThesesFilter";
import { ThesisTypeFilter, getThesesList } from "../../backend_callers";

type Props = {
	// currentThesesList: Thesis[],
};

type State = {
	thesesList: Thesis[],
};

function formatEmployeeDisplayName(employee: Employee): string {
	const fullName = `${employee.user.first_name} ${employee.user.last_name}`;
	return employee.title ? `${employee.title} ${fullName}` : fullName;
}

function formatThesisKind(kind: ThesisKind): string {
	switch (kind) {
		case ThesisKind.Masters: return "mgr";
		case ThesisKind.Engineers: return "inż";
		case ThesisKind.Bachelors: return "lic";
		case ThesisKind.BachelorsEngineers: return "lic+inż";
		case ThesisKind.Isim: return "ISIM";
	}
}

const TABLE_COL_DECLS: Column[] = [{
	id: "isThesisReserved",
	Header: "Rezerwacja",
	accessor: (props: Thesis) => props.reserved,
	Cell: props => <ReservationIndicator reserved={props.value} />,
	width: 100,
	filterable: false,
}, {
	id: "thesisKind",
	Header: "Typ",
	accessor: (props: Thesis) => formatThesisKind(props.kind),
	filterable: false,
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
	public constructor(props: {}) {
		super(props);
		this.state = {
			thesesList: [],
		};
		this.initListForTypeFilter(ThesisTypeFilter.Default);
	}

	private async initListForTypeFilter(filter: ThesisTypeFilter): Promise<void> {
		const theses = await getThesesList(filter);
		this.setState({ thesesList: theses });
	}

	public render() {
		return <div>
			<ThesesFilter
				onChanged={this.onTypeFilterChanged}
				initialValue={ThesisTypeFilter.Default}
			/>
			<br />
			<ReactTable
				key="table"
				className={"-striped -highlight"}
				data={this.state.thesesList}
				columns={TABLE_COL_DECLS}
				defaultPageSize={10}
				getTableProps={getTableProps}
				getTheadProps={getTheadProps}
				// getTrProps={getTrProps}
				style={{
					height: "400px"
				}}
			/>
		</div>;
	}

	private onTypeFilterChanged = (newFilter: ThesisTypeFilter): void => {
		this.initListForTypeFilter(newFilter);
	}
}
