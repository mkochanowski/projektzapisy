import * as React from "react";
import Griddle, { ColumnMetaData } from "griddle-react";

import { ListLoadingIndicator } from "./ListLoadingIndicator";
import { ReservationIndicator } from "./ReservationIndicator";
import { ThesisTypeFilter } from "../backend_callers";
import { Thesis, ThesisStatus, ThesisKind } from "../types";
import { ApplicationState } from "../types/application_state";
import { TopFilters } from "./TopFilters";

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

const THESES_PER_PAGE = 10;
const GRIDDLE_NO_DATA = "Brak wyników";
const GRIDDLE_FILTER_MAGIC = "a hack of epic proportions";

// Converted theses data passed to griddle for rendering
type GriddleThesisData = {
	id: number;
	reserved: boolean;
	title: string;
	advisorName: string;
};

type Props = {
	applicationState: ApplicationState;
	thesesList: Thesis[];

	thesisForId: (id: number) => Thesis | null;
	onThesisClicked: (t: Thesis) => void;
};

const initialState = {
	typeFilter: ThesisTypeFilter.Default,
	titleFilter: "",
	advisorFilter: "",
};
type State = typeof initialState;

export class ThesesTable extends React.Component<Props> {
	private griddle: any;
	state = initialState;

	private setGriddle = (griddle: Griddle<any>) => {
		this.griddle = griddle;
	}

	private setStateAsync<K extends keyof State>(partialState: Pick<State, K>): Promise<void> {
		return new Promise((resolve, _) => {
			this.setState(partialState, resolve);
		});
	}

	private renderTopFilters() {
		return <TopFilters
			onTypeChange={this.onTypeFilterChanged}
			typeValue={this.state.typeFilter}
			onAdvisorChange={this.onAdvisorFilterChanged}
			advisorValue={this.state.advisorFilter}
			onTitleChange={this.onTitleFilterChanged}
			titleValue={this.state.titleFilter}
			enabled={this.props.applicationState === ApplicationState.Normal}
		/>;
	}

	private getTableCss(): React.CSSProperties {
		return (
			this.props.applicationState === ApplicationState.PerformingBackendChanges
			? { opacity: 0.5, pointerEvents: "none" } : { }
		);
	}

	private renderThesesList() {
		const style = this.getTableCss();
		const isLoading = this.props.applicationState === ApplicationState.InitialLoading;
		return <div style={style}>
			<Griddle
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
				// @ts-ignore - missing prop
				allowEmptyGrid={isLoading}
				// Hacky: you don't have to set useExternalData for this stuff to work
				externalIsLoading={isLoading}
				externalLoadingComponent={ListLoadingIndicator}
			/>
		</div>;
	}

	public render() {
		return (
			<>
				{this.renderTopFilters()}
				<br />
				{this.renderThesesList()}
			</>
		);
	}

	private getTableResults(): GriddleThesisData[] {
		const griddleResults = this.props.thesesList.map(thesis => ({
			id: thesis.id,
			reserved: thesis.reserved,
			title: thesis.title,
			advisorName: thesis.advisor ? thesis.advisor.displayName : "<brak>",
		}));
		return this.filterGriddleResults(griddleResults);
	}

	private onRowClick = (row: any, _e: MouseEvent) => {
		const data: GriddleThesisData = row.props.data;
		const thesis = this.props.thesisForId(data.id);
		if (!thesis) {
			console.warn(`[Table onclick] Griddle had bad thesis ID ${data.id}`);
			return;
		}
		this.props.onThesisClicked(thesis);
	}

	private filterGriddleResults(results: GriddleThesisData[]) {
		const advisor = this.state.advisorFilter;
		const title = this.state.titleFilter;
		const type = this.state.typeFilter;

		return results.filter(td => {
			const thesis = this.props.thesisForId(td.id);
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

	// See setGriddleFilter
	private griddleFilterer = (results: GriddleThesisData[], filter: any) => {
		if (filter !== GRIDDLE_FILTER_MAGIC) {
			return results;
		}
		return this.filterGriddleResults(results);
	}

	private setGriddleFilter() {
		// This is a rather big hack to achieve what we want;
		// I want the filters in external components I manage myself; when
		// the value is changed I just want to tell griddle to update itself
		// we use a ref to save the component instance and call the internal setFilter
		// method; this forces griddle to call the (user supplied) custom filtering method
		// where I apply the new filters
		// To be able to tell whether it's me who called my custom filter method
		// I pass this "magic" filter argument; in the handler I only use it to check
		// if it was me who called it, the filters are saved on `this`
		this.griddle.setFilter(GRIDDLE_FILTER_MAGIC);
		// Changing a filter will almost certainly change the result set,
		// so it'd be nice to scroll to the top but griddle won't do that itself, so...
		document.querySelector("div.griddle > div > div > div > div")!.scrollTop = 0;
	}

	private onTypeFilterChanged = async (newFilter: ThesisTypeFilter) => {
		await this.setStateAsync({ typeFilter: newFilter });
		this.setGriddleFilter();
	}

	private onAdvisorFilterChanged = async (newAdvisorFilter: string) => {
		if (!newAdvisorFilter.trim()) {
			newAdvisorFilter = "";
		}
		await this.setStateAsync({ advisorFilter: newAdvisorFilter });
		this.setGriddleFilter();
	}

	private onTitleFilterChanged = async (newTitleFilter: string) => {
		if (!newTitleFilter.trim()) {
			newTitleFilter = "";
		}
		await this.setStateAsync({ titleFilter: newTitleFilter });
		this.setGriddleFilter();
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
