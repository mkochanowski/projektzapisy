import * as React from "react";
import Griddle, { ColumnMetaData } from "griddle-react";

import { Thesis/*, ThesisKind, thesisKindToString*/ } from "../types";
// import { ReservationIndicator } from "./ReservationIndicator";
import { TopFilters } from "./TopFilters";
import { ThesisTypeFilter, getThesesList, SortColumn } from "../backend_callers";
// import { isThesisAvailable } from "../utils";
// import { ListLoadingIndicator } from "./ListLoadingIndicator";
import { ThesisDetails } from "./ThesisDetails";
import { ListLoadingIndicator } from "./ListLoadingIndicator";
import { ReservationIndicator } from "./ReservationIndicator";

// const reactTableLocalization = {
// 	previousText: "Poprzednia",
// 	nextText: "Następna",
// 	loadingText: "Ładowanie...",
// 	noDataText: "Brak wierszy",
// 	pageText: "Strona",
// 	ofText: "z",
// 	rowsText: "wierszy",
// };

// const TABLE_COL_DECLS: Column[] = [{
// 	id: "isThesisReserved",
// 	Header: "Rezerwacja",
// 	accessor: (props: Thesis) => props.reserved,
// 	Cell: props => <ReservationIndicator reserved={props.value} />,
// 	width: 100,
// 	filterable: false,
// }, {
// 	id: "thesisKind",
// 	Header: "Typ",
// 	accessor: (props: Thesis) => thesisKindToString(props.kind),
// 	filterable: false,
// 	width: 80,
// }, {
// 	id: "thesisAdvisor",
// 	Header: "Promotor",
// 	accessor: (props: Thesis) => props.advisor ? props.advisor.displayName : "<brak>",
// 	filterable: true,
// }, {
// 	id: "thesisName",
// 	Header: "Tytuł",
// 	accessor: (props: Thesis) => props.title,
// 	filterable: true,
// }];

// function getTableProps() {
// 	return { style: { textAlign: "center" } };
// }

// function getTheadProps() {
// 	return { style: {
// 		fontWeight: "bold",
// 		fontSize: "120%",
// 	}};
// }

const griddleColumnMeta: Array<ColumnMetaData<any>> = [
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

// ACHTUNG must match value in views.py
const THESES_PER_PAGE = 10;

type Props = {};

type State = {
	selectedThesis: Thesis | null;
	currentTypeFilter: ThesisTypeFilter;
	currentTitleFilter: string;
	currentAdvisorFilter: string;

	maxTablePage: number;
	currentTablePage: number;
	thesesList: Thesis[];
	tableSortColumn: string;
	isLoadingTable: boolean;
	isTableAscendingSort: boolean;
};

const initialState: State = {
	selectedThesis: null,

	currentTypeFilter: ThesisTypeFilter.Default,
	currentTitleFilter: "",
	currentAdvisorFilter: "",

	maxTablePage: 0,
	currentTablePage: 1,
	thesesList: [],
	tableSortColumn: "",
	isLoadingTable: false,
	isTableAscendingSort: false,
};

export class ThesesApp extends React.Component<Props, State> {
	state = initialState;
	private lastGriddleSetPage: number = 0;

	async componentDidMount() {
		this.updateWithNewState(this.state);
	}

	private renderTopFilters() {
		return <TopFilters
			onTypeChange={this.onTypeFilterChanged}
			initialTypeValue={this.state.currentTypeFilter}
			onAdvisorChange={this.onAdvisorFilterChanged}
			initialAdvisorValue={this.state.currentAdvisorFilter}
			onTitleChange={this.onTitleFilterChanged}
			initialTitleValue={this.state.currentTitleFilter}
		/>;
	}

	private renderThesesList() {
		// return <ReactTable
		// 	key="table"
		// 	ref={this.assignReactTable}
		// 	className={"-striped -highlight"}
		// 	defaultPageSize={10}
		// 	getTableProps={getTableProps}
		// 	getTheadProps={getTheadProps}
		// 	getTdProps={this.getTdProps}
		// 	style={{
		// 		height: "400px"
		// 	}}
		// 	{...reactTableLocalization}
		// 	columns={TABLE_COL_DECLS}
		// 	data={this.props.thesesList}
		// 	pages={-1}
		// 	loading={this.props.isLoadingList}
		// 	manual
		// />;
		return <Griddle
			useGriddleStyles={false}
			tableClassName={"griddleTable"}
			showFilter={false}
			enableInfiniteScroll
			infiniteScrollLoadTreshold={25}
			useFixedHeader
			bodyHeight={200}
			resultsPerPage={THESES_PER_PAGE}
			onRowClick={(this.onRowClick as any)}
			columnMetadata={griddleColumnMeta}
			// rowMetadata={{ key: "id" } as any}
			metadataColumns={["id"]}
			results={this.getTableResults()}

			useExternal
			externalSetPage={this.setTablePage}
			externalChangeSort={this.setTableSort}
			// tslint:disable:no-empty
			// This is stupid as in external mode it can only ever
			// "set" the page size to the prop we specify ourselves
			externalSetPageSize={function() {}}
			// ...and this is hopelessly broken in 0.8.2, courtesy
			// mr Dan Krieger commit 60338690404adddecf41427a32cd210b7273403d
			// in componentWillReceiveProps, if the results prop changed
			// he fires setFilter - which will obviously fetch new results
			// and change the prop, and so you get an infinite render loop
			externalSetFilter={function() {}}
			// tslint:enable:no-empty
			externalMaxPage={this.state.maxTablePage}
			externalCurrentPage={this.state.currentTablePage}
			externalIsLoading={this.state.isLoadingTable}
			externalSortColumn={this.state.tableSortColumn}
			externalSortAscending={this.state.isTableAscendingSort}
			externalLoadingComponent={ListLoadingIndicator}
		/>;
	}

	private getTableResults() {
		console.error("GET RESULTS");
		return this.state.thesesList.map(thesis => ({
			id: thesis.id,
			reserved: thesis.reserved,
			title: thesis.title,
			advisorName: thesis.advisor ? thesis.advisor.displayName : "<brak>",
		}));
	}

	private setTablePage = (index: number) => {
		console.warn("Set page to", index);
		// Griddle has no throttling mechanism and will call
		// this a massive number of times in a very short time period;
		// the react state is only updated when we get a successful server response,
		// so all those redundant griddle requests would be made before that happens
		// so we need a separate realtime-updated field
		if (this.lastGriddleSetPage === index) {
			return;
		}
		this.lastGriddleSetPage = index;
		this.updateWithNewState({ currentTablePage: index });
	}

	private setTableSort = (sortColumnStr: string | undefined, isAscending: boolean) => {
		this.updateWithNewState({
			tableSortColumn: sortColumnStr || "", isTableAscendingSort: isAscending,
		});
	}

	private onTypeFilterChanged = (newFilter: ThesisTypeFilter): void => {
		this.updateFreshWithNewState({
			currentTypeFilter: newFilter,
		});
	}

	private onAdvisorFilterChanged = (newAdvisorFilter: string): void => {
		this.updateFreshWithNewState({
			currentAdvisorFilter: newAdvisorFilter,
		});
	}

	private onTitleFilterChanged = (newTitleFilter: string): void => {
		this.updateFreshWithNewState({
			currentTitleFilter: newTitleFilter,
		});
	}

	private async updateFreshWithNewState<T extends keyof State>(partialState: Pick<State, T>) {
		await this.updateWithNewState(Object.assign(partialState, {
			thesesList: [],
			currentTablePage: 1,
			lastGriddleSetPage: 1,
		}));
		// Griddle is such a piece of shit
		document.querySelector("div.griddle > div > div > div > div")!.scrollTop = 0;
	}

	private async updateWithNewState<T extends keyof State>(partialState: Pick<State, T>) {
		console.warn("Updating with new state");
		const newState = Object.assign({}, this.state, partialState);
		const newList = await getThesesListForState(newState);
		newState.thesesList.push(...newList.theses);
		newState.maxTablePage = Math.ceil(newList.total / THESES_PER_PAGE);
		this.setState(newState);
	}

	private onRowClick = (row: any, e: MouseEvent) => {
		console.warn(row, e);
	}

	public render() {
		const mainComponent = (
			<>
				{this.renderTopFilters()}
				<br />
				{this.renderThesesList()}
			</>
		);
		return this.state.selectedThesis
			? <>
				{mainComponent}
				<br />,
				<hr />,
				<ThesisDetails
					key="thesis_details"
					selectedThesis={this.state.selectedThesis}
					onModifiedThesisSaved={this.handleThesisSaved}
				/>
			</>
			: mainComponent;
	}

	// Must be on the instance, we need a closure for `this`
	/*private getTdProps = (_state: any, rowInfo: RowInfo | undefined, _column: any) => {
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
				// events like expanding SubComponents and; pivots.
				// By default a custom "onClick" handler; will; override; this; functionality.;
				if (handleOriginal) {
					handleOriginal();
				}
			}
		};
	}*/

	private handleThesisSaved = () => {
		console.warn("SAVED");
		return Promise.resolve();
	}
}

function sortColumnFromString(sortColumnStr: string): SortColumn {
	switch (sortColumnStr) {
		case "title":
			return SortColumn.ThesisTitle;
		case "advisor":
			return SortColumn.ThesisAdvisor;
		default:
			return SortColumn.None;
	}
}

async function getThesesListForState(state: State) {
	return getThesesList(
		state.currentTypeFilter, state.currentTitleFilter, state.currentAdvisorFilter,
		state.currentTablePage,
	);
}
