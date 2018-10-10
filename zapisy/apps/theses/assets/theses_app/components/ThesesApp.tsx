import * as React from "react";
import Griddle, { ColumnMetaData } from "griddle-react";

import { Thesis, ThesisStatus, ThesisKind } from "../types";
import { TopFilters } from "./TopFilters";
import { ThesisTypeFilter, getThesesList } from "../backend_callers";
import { ThesisDetails } from "./ThesisDetails";
import { ReservationIndicator } from "./ReservationIndicator";
import { ListLoadingIndicator } from "./ListLoadingIndicator";

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

const GRIDDLE_NO_DATA = "Brak danych";

// ACHTUNG must match value in views.py
const THESES_PER_PAGE = 10;

type Props = {};

type State = {
	selectedThesis: Thesis | null;
	currentTypeFilter: ThesisTypeFilter;
	currentTitleFilter: string;
	currentAdvisorFilter: string;

	thesesList: Thesis[];
	isLoadingThesesList: boolean;
};

const initialState: State = {
	selectedThesis: null,

	currentTypeFilter: ThesisTypeFilter.Default,
	currentTitleFilter: "",
	currentAdvisorFilter: "",

	thesesList: [],
	isLoadingThesesList: true,
};

type GriddleThesisData = {
	id: number;
	reserved: boolean;
	title: string;
	advisorName: string;
};

const GRIDDLE_FILTER_MAGIC = "a hack of epic proportions";

export class ThesesApp extends React.Component<Props, State> {
	state = initialState;
	private griddle: any;

	async componentDidMount() {
		await this.setStateAsync({
			thesesList: await getThesesList(),
			isLoadingThesesList: false,
		});
		this.setGriddleFilter();
	}

	private setStateAsync<K extends keyof State>(partialState: Pick<State, K>): Promise<void> {
		return new Promise((resolve, _) => {
			this.setState(partialState, resolve);
		});
	}

	private renderTopFilters() {
		return <TopFilters
			onTypeChange={this.onTypeFilterChanged}
			typeValue={this.state.currentTypeFilter}
			onAdvisorChange={this.onAdvisorFilterChanged}
			advisorValue={this.state.currentAdvisorFilter}
			onTitleChange={this.onTitleFilterChanged}
			titleValue={this.state.currentTitleFilter}
			enabled={!this.state.isLoadingThesesList}
		/>;
	}

	private setGriddle = (griddle: Griddle<any>) => {
		this.griddle = griddle;
	}

	private griddleFilterer = (results: GriddleThesisData[], filter: any) => {
		if (filter !== GRIDDLE_FILTER_MAGIC) {
			return results;
		}
		const advisor = this.state.currentAdvisorFilter;
		const title = this.state.currentTitleFilter;
		const type = this.state.currentTypeFilter;

		return results.filter(td => {
			const thesis = this.state.thesesList.find(t => t.id === td.id);
			if (!thesis) {
				console.warn("[Sort] Griddle table has bad thesis", td);
				return false;
			}
			return (
				thesisMatchesType(thesis, type) &&
				(!advisor || td.advisorName.toLowerCase().includes(advisor.toLowerCase())) &&
				(!title || td.title.toLowerCase().includes(title.toLowerCase()))
			);
		});
	}

	private renderThesesList() {
		return <Griddle
			ref={this.setGriddle}
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
			metadataColumns={["id"]}
			results={this.getTableResults()}
			noDataMessage={GRIDDLE_NO_DATA}
			useCustomFilterer={true}
			customFilterer={this.griddleFilterer}
			// Hacky: you don't have to set useExternalData for this stuff to work
			externalIsLoading={this.state.isLoadingThesesList}
			externalLoadingComponent={ListLoadingIndicator}
			// @ts-ignore - missing prop
			allowEmptyGrid={this.state.isLoadingThesesList}
		/>;
	}

	private getTableResults(): GriddleThesisData[] {
		console.error("GET RESULTS", this.state.thesesList);
		return this.state.thesesList.map(thesis => ({
			id: thesis.id,
			reserved: thesis.reserved,
			title: thesis.title,
			advisorName: thesis.advisor ? thesis.advisor.displayName : "<brak>",
		}));
	}

	private setGriddleFilter() {
		this.griddle.setFilter(GRIDDLE_FILTER_MAGIC);
	}

	private onTypeFilterChanged = async (newFilter: ThesisTypeFilter) => {
		await this.setStateAsync({ currentTypeFilter: newFilter });
		this.setGriddleFilter();
	}

	private onAdvisorFilterChanged = async (newAdvisorFilter: string) => {
		if (!newAdvisorFilter.trim()) {
			newAdvisorFilter = "";
		}
		await this.setStateAsync({ currentAdvisorFilter: newAdvisorFilter });
		this.setGriddleFilter();
	}

	private onTitleFilterChanged = async (newTitleFilter: string) => {
		if (!newTitleFilter.trim()) {
			newTitleFilter = "";
		}
		await this.setStateAsync({ currentTitleFilter: newTitleFilter });
		this.setGriddleFilter();
	}

	private onRowClick = (row: any, _e: MouseEvent) => {
		const data: GriddleThesisData = row.props.data;
		const thesis = this.state.thesesList.find(t => t.id === data.id);
		if (!thesis) {
			console.warn("[Click] Griddle table has bad thesis", data);
			return;
		}
		this.setState({
			selectedThesis: thesis,
		});
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
					selectedThesis={this.state.selectedThesis}
					onModifiedThesisSaved={this.handleThesisSaved}
				/>
			</>
			: mainComponent;
	}

	private handleThesisSaved = () => {
		console.warn("SAVED");
		return Promise.resolve();
	}
}

function isThesisAvailable(thesis: Thesis): boolean {
	return (
		thesis.status !== ThesisStatus.InProgress &&
		thesis.status !== ThesisStatus.Defended &&
		!thesis.reserved
	);
}

function thesisMatchesType(thesis: Thesis, type: ThesisTypeFilter) {
	switch (type) {
		case ThesisTypeFilter.All: return true;
		case ThesisTypeFilter.AllCurrent: return isThesisAvailable(thesis);
		case ThesisTypeFilter.Masters: return thesis.kind === ThesisKind.Masters;
		case ThesisTypeFilter.Engineers: return thesis.kind === ThesisKind.Engineers;
		case ThesisTypeFilter.Bachelors: return thesis.kind === ThesisKind.Bachelors;
		case ThesisTypeFilter.BachelorsISIM: return thesis.kind === ThesisKind.Isim;
		case ThesisTypeFilter.AvailableMasters:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Masters;
		case ThesisTypeFilter.AvailableEngineers:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Engineers;
		case ThesisTypeFilter.AvailableBachelors:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Bachelors;
		case ThesisTypeFilter.AvailableBachelorsISIM:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Isim;
	}
}
