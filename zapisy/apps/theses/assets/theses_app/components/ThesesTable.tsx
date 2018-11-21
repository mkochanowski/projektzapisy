import * as React from "react";
import Griddle, { ColumnMetaData } from "griddle-react";

import { ListLoadingIndicator } from "./ListLoadingIndicator";
import { ReservationIndicator } from "./ReservationIndicator";
import { ThesisTypeFilter } from "../backend_callers";
import { Thesis } from "../types";
import { ApplicationState } from "../types/application_state";

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
	advisorFilter: string;
	titleFilter: string;
	typeFilter: ThesisTypeFilter;
	applicationState: ApplicationState;

	thesisForId: (id: number) => Thesis;
}

export class ThesesTable extends React.Component<Props> {
	private griddle: any;

	private setGriddle = (griddle: Griddle<any>) => {
		this.griddle = griddle;
	}

	private filterGriddleResults(results: GriddleThesisData[]) {
		const advisor = this.props.advisorFilter;
		const title = this.props.titleFilter;
		const type = this.props.typeFilter;

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

	private getTableCss(): React.CSSProperties {
		return (
			this.props.applicationState === ApplicationState.PerformingBackendChanges
			? { opacity: 0.5, pointerEvents: "none" } : { }
		);
	}

	private renderThesesList() {
		const { applicationState } = this.props;
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

	private getTableResults(): GriddleThesisData[] {
		const griddleResults = this.state.thesesList.map(thesis => ({
			id: thesis.id,
			reserved: thesis.reserved,
			title: thesis.title,
			advisorName: thesis.advisor ? thesis.advisor.displayName : "<brak>",
		}));
		return this.filterGriddleResults(griddleResults);
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
