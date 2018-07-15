import * as React from "react";
import ReactTable, { Column, RowInfo, ComponentPropsGetter0 } from "react-table";
import "react-table/react-table.css";

import { Thesis, Employee, ThesisKind } from "../../types";
import { ReservationIndicator } from "./ReservationIndicator";
import { SearchBox } from "./SearchBox";
import { ThesesFilter } from "./ThesesFilter";
import { ThesisTypeFilter, getThesesList } from "../../backend_callers";
import { isThesisAvailable } from "../../utils";
import { ListLoadingIndicator } from "./ListLoadingIndicator";
import { awaitSleep } from "common/utils";

type Props = {
	thesesList: Thesis[],
};

type State = {
	currentListFilter: ThesisTypeFilter,
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

function getTdProps(_: any, rowInfo: RowInfo | undefined, column: any) {
	if (!rowInfo) {
		return {};
	}
	return {
		style: {
			cursor: "pointer",
		},
		onClick: (e: any, handleOriginal: any) => {
		  console.log("A Td Element was clicked!");
		  console.log("it produced this event:", e);
		  console.log("It was in this column:", column);
		  console.log("It was in this row:", rowInfo);

		  // IMPORTANT! React-Table uses onClick internally to trigger
		  // events like expanding SubComponents and pivots.
		  // By default a custom 'onClick' handler will override this functionality.
		  // If you want to fire the original onClick handler, call the
		  // 'handleOriginal' function.
		  if (handleOriginal) {
			handleOriginal();
		  }
		}
	};
}

export class ThesesList extends React.Component<Props, State> {
	public constructor(props: Props) {
		super(props);
		this.state = {
			currentListFilter: ThesisTypeFilter.Default,
		};
	}

	public render() {
		return this.props.thesesList.length ?
			<div>
				<ThesesFilter
					onChanged={this.onTypeFilterChanged}
					initialValue={ThesisTypeFilter.Default}
				/>
				<br />
				<ReactTable
					key="table"
					className={"-striped -highlight"}
					data={this.computeFilteredThesesList()}
					columns={TABLE_COL_DECLS}
					defaultPageSize={10}
					getTableProps={getTableProps}
					getTheadProps={getTheadProps}
					getTdProps={getTdProps}
					style={{
						height: "400px"
					}}
				/>
			</div>
			:
			<ListLoadingIndicator />;
	}

	private computeFilteredThesesList(): Thesis[] {
		return this.props.thesesList.filter(thesis => {
			switch (this.state.currentListFilter) {
				case ThesisTypeFilter.All: return true;
				case ThesisTypeFilter.AllCurrent:
					return isThesisAvailable(thesis);
				case ThesisTypeFilter.AvailableBachelors:
					return thesis.kind === ThesisKind.Bachelors && isThesisAvailable(thesis);
				case ThesisTypeFilter.AvailableBachelorsISIM:
					return thesis.kind === ThesisKind.Isim && isThesisAvailable(thesis);
				case ThesisTypeFilter.AvailableEngineers:
					return thesis.kind === ThesisKind.Engineers && isThesisAvailable(thesis);
				case ThesisTypeFilter.AvailableMasters:
					return thesis.kind === ThesisKind.Masters && isThesisAvailable(thesis);
				case ThesisTypeFilter.Bachelors:
					return thesis.kind === ThesisKind.Bachelors;
				case ThesisTypeFilter.BachelorsISIM:
					return thesis.kind === ThesisKind.Isim;
				case ThesisTypeFilter.Engineers:
					return thesis.kind === ThesisKind.Engineers;
				case ThesisTypeFilter.Masters:
					return thesis.kind === ThesisKind.Masters;
			}
			return false;
		});
	}

	private onTypeFilterChanged = (newFilter: ThesisTypeFilter): void => {
		this.setState({
			currentListFilter: newFilter,
		});
	}
}
