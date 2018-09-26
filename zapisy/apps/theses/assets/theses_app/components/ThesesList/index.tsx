import * as React from "react";
import ReactTable, { Column, RowInfo } from "react-table";
import "react-table/react-table.css";

import { Thesis, ThesisKind, thesisKindToString } from "../../types";
import { ReservationIndicator } from "./ReservationIndicator";
import { TopFilters } from "./TopFilters";
import { ThesisTypeFilter } from "../../backend_callers";
import { isThesisAvailable } from "../../utils";
import { ListLoadingIndicator } from "./ListLoadingIndicator";

const reactTableLocalization = {
	previousText: "Poprzednia",
	nextText: "Następna",
	loadingText: "Ładowanie...",
	noDataText: "Brak wierszy",
	pageText: "Strona",
	ofText: "z",
	rowsText: "wierszy",
};

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
	accessor: (props: Thesis) => thesisKindToString(props.kind),
	filterable: false,
	width: 80,
}, {
	id: "thesisAdvisor",
	Header: "Promotor",
	accessor: (props: Thesis) => props.advisor ? props.advisor.displayName : "<brak>",
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

type Props = {
	thesesList: Thesis[],
	thesisClickCallback: (thesis: Thesis) => void,
};

const initialState = {
	currentListFilter: ThesisTypeFilter.Default,
	currentTitleFilter: "",
	currentAdvisorFilter: "",
};

type State = typeof initialState;

export class ThesesList extends React.Component<Props, State> {
	private reactTable: ReactTable | null = null;
	state = initialState;

	private assignReactTable = (table: ReactTable): void => {
		this.reactTable = table;
	}

	public render() {
		return this.props.thesesList.length ?
			<>
				<TopFilters
					onTypeChange={this.onTypeFilterChanged}
					typeValue={this.state.currentListFilter}
					onAdvisorChange={this.onAdvisorFilterChanged}
					advisorValue={this.state.currentAdvisorFilter}
					onTitleChange={this.onTitleFilterChanged}
					titleValue={this.state.currentTitleFilter}
				/>
				<br />
				<ReactTable
					key="table"
					ref={this.assignReactTable}
					className={"-striped -highlight"}
					data={this.computeFilteredThesesList()}
					columns={TABLE_COL_DECLS}
					defaultPageSize={10}
					getTableProps={getTableProps}
					getTheadProps={getTheadProps}
					getTdProps={this.getTdProps}
					style={{
						height: "400px"
					}}
					{...reactTableLocalization}
				/>
			</>
			:
			<ListLoadingIndicator />;
	}

	// Must be on the instance, we need a closure for `this`
	private getTdProps = (_state: any, rowInfo: RowInfo | undefined, _column: any) => {
		if (!rowInfo) {
			return {};
		}
		return {
			style: {
				cursor: "pointer",
			},
			onClick: (_event: any, handleOriginal: () => void) => {
				console.warn("Click in row", rowInfo);
				this.props.thesisClickCallback(rowInfo.original);
				// React-Table uses onClick internally to trigger
				// events like expanding SubComponents and pivots.
				// By default a custom 'onClick' handler will override this functionality.
				if (handleOriginal) {
					handleOriginal();
				}
			}
		};
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

	private onAdvisorFilterChanged = (newAdvisorFilter: string): void => {
		this.setState({
			currentAdvisorFilter: newAdvisorFilter,
		});
	}

	private onTitleFilterChanged = (newTitleFilter: string): void => {
		this.setState({
			currentTitleFilter: newTitleFilter,
		});
	}
}
