import * as React from "react";
import Griddle, { ColumnMetaData } from "griddle-react";

import { Thesis, ThesisStatus, ThesisKind } from "../types";
import { TopFilters } from "./TopFilters";
import { ThesisTypeFilter, getThesesList, saveModifiedThesis } from "../backend_callers";
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

const GRIDDLE_NO_DATA = "Brak wyników";

// ACHTUNG must match value in views.py
const THESES_PER_PAGE = 10;

const enum ApplicationState {
	InitialLoading,
	PerformingBackendChanges,
	Normal,
}

type Props = {};

type State = {
	selectedThesis: Thesis | null;
	currentTypeFilter: ThesisTypeFilter;
	currentTitleFilter: string;
	currentAdvisorFilter: string;

	thesesList: Thesis[];
	applicationState: ApplicationState,
};

const initialState: State = {
	selectedThesis: null,

	currentTypeFilter: ThesisTypeFilter.Default,
	currentTitleFilter: "",
	currentAdvisorFilter: "",

	thesesList: [],
	applicationState: ApplicationState.InitialLoading,
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
		this.setState({
			thesesList: await getThesesList(),
			applicationState: ApplicationState.Normal,
		});
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
			enabled={this.state.applicationState === ApplicationState.Normal}
		/>;
	}

	private setGriddle = (griddle: Griddle<any>) => {
		this.griddle = griddle;
	}

	private filterGriddleResults(results: GriddleThesisData[]) {
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

	// See setGriddleFilter
	private griddleFilterer = (results: GriddleThesisData[], filter: any) => {
		if (filter !== GRIDDLE_FILTER_MAGIC) {
			return results;
		}
		return this.filterGriddleResults(results);
	}

	private renderThesesList() {
		const { applicationState } = this.state;
		const style: React.CSSProperties = (
			applicationState === ApplicationState.PerformingBackendChanges
			? { opacity: 0.5, pointerEvents: "none" } : { }
		);
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
				allowEmptyGrid={applicationState === ApplicationState.InitialLoading}
				// Hacky: you don't have to set useExternalData for this stuff to work
				externalIsLoading={applicationState === ApplicationState.InitialLoading}
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

	private getThesisForId(id: number, theses: Thesis[] = this.state.thesesList): Thesis | null {
		return theses.find(t => t.id === id) || null;
	}

	private onRowClick = (row: any, _e: MouseEvent) => {
		const data: GriddleThesisData = row.props.data;
		const thesis = this.getThesisForId(data.id);
		if (!thesis) {
			console.warn(`[Table onclick] Griddle had bad thesis ID ${data.id}`);
		}
		this.setState({ selectedThesis: thesis });
	}

	public render() {
		console.warn("Main render");
		const mainComponent = (
			<>
				{this.renderTopFilters()}
				<br />
				{this.renderThesesList()}
			</>
		);
		const { selectedThesis } = this.state;
		return selectedThesis !== null
			? <>
				{mainComponent}
				<br />
				<hr />
				<ThesisDetails
					selectedThesis={selectedThesis}
					onSaveRequested={this.handleThesisSave}
					isSaving={this.state.applicationState === ApplicationState.PerformingBackendChanges}
				/>
			</>
			: mainComponent;
	}

	private handleThesisSave = async (modifiedThesis: Thesis) => {
		const { selectedThesis } = this.state;
		if (selectedThesis === null) {
			console.warn("Tried to save thesis but none selected, this shouldn't happen");
			return;
		}
		this.setState({ applicationState: ApplicationState.PerformingBackendChanges });
		const oldSelectedThesisId = selectedThesis.id;
		try {
			await saveModifiedThesis(selectedThesis, modifiedThesis);
		} catch (err) {
			alert(
				"Nie udało się zapisać pracy. Spróbuj jeszcze raz. " +
				"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów"
			);
			return;
		}
		// This could theoretically be null if someone deletes what we've just saved
		// slim chance but who knows
		const newList = await getThesesList();
		const newThesisInstance = this.getThesisForId(oldSelectedThesisId, newList);
		this.setState({
			thesesList: newList,
			applicationState: ApplicationState.Normal,
			selectedThesis: newThesisInstance,
		});
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
