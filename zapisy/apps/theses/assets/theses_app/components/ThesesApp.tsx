import * as React from "react";
import Griddle from "griddle-react";

import { Thesis/*, ThesisKind, thesisKindToString*/ } from "../types";
// import { ReservationIndicator } from "./ReservationIndicator";
import { TopFilters } from "./TopFilters";
import { ThesisTypeFilter } from "../backend_callers";
// import { isThesisAvailable } from "../utils";
// import { ListLoadingIndicator } from "./ListLoadingIndicator";
import { ThesisDetails } from "./ThesisDetails";

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

type Props = {};

const initialState = {
	selectedThesis: null as (Thesis | null),

	currentTypeFilter: ThesisTypeFilter.Default,
	currentTitleFilter: "",
	currentAdvisorFilter: "",
};

type State = typeof initialState;

export class ThesesApp extends React.Component<Props, State> {
	state = initialState;

	public constructor(props: Props) {
		super(props);
	}

	private renderTopFilters() {
		return <TopFilters
			onTypeChange={this.onTypeFilterChanged}
			typeValue={this.state.currentTypeFilter}
			onAdvisorChange={this.onAdvisorFilterChanged}
			advisorValue={this.state.currentAdvisorFilter}
			onTitleChange={this.onTitleFilterChanged}
			titleValue={this.state.currentTitleFilter}
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
			results={
				[
					{ one: "one", two: "two", three: "three" },
					{ one: "uno", two: "dos", three: "tres" },
					{ one: "ichi", two: "ni", three: "san" },
				]
			}
		/>;
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

	private onTypeFilterChanged = (newFilter: ThesisTypeFilter): void => {
		this.setState({
			currentTypeFilter: newFilter,
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
