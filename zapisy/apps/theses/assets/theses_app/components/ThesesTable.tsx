import * as React from "react";
import * as Mousetrap from "mousetrap";
import Griddle from "griddle-react";

import { ListLoadingIndicator } from "./ListLoadingIndicator";
import { ThesisTypeFilter } from "../backend_callers";
import { Thesis, ThesisStatus, ThesisKind, BasePerson } from "../types";
import { ApplicationState } from "../types/application_state";
import { TopFilters } from "./TopFilters";
import { strcmp } from "common/utils";
import {
	THESES_PER_PAGE, griddleColumnMeta, GRIDDLE_NO_DATA, GriddleThesisData,
} from "./GriddleDetails";

type Props = {
	applicationState: ApplicationState;
	thesesList: Thesis[];
	isEditingThesis: boolean;

	thesisForId: (id: number) => Thesis | null;
	onThesisClicked: (t: Thesis) => void;
};

const initialState = {
	typeFilter: ThesisTypeFilter.Default,
	titleFilter: "",
	advisorFilter: "",
	griddlePage: 1,
	sortAscending: true,
	sortColumn: "" as ("title" | "advisorName" | ""),
};
type State = typeof initialState;

export class ThesesTable extends React.Component<Props, State> {
	state = initialState;
	private filterCache: Map<string, Thesis[]> = new Map();
	private sortCache: Map<string, Thesis[]> = new Map();

	componentDidMount() {
		this.installKeyHandler();
	}

	componentWillUnmount() {
		this.uninstallKeyHandler();
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
		const data = this.getData();
		const maxPage = Math.ceil(data.length / THESES_PER_PAGE);
		return <div style={style}>
			<Griddle
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
				results={this.dataForGriddle(data)}
				noDataMessage={GRIDDLE_NO_DATA}
				// @ts-ignore - missing prop
				allowEmptyGrid={isLoading}
				useExternal
				externalIsLoading={isLoading}
				externalLoadingComponent={ListLoadingIndicator}
				externalSetPage={this.setPage}
				externalSetPageSize={() => void(0)}
				externalChangeSort={this.changeSort}
				externalSetFilter={() => void(0)}
				externalCurrentPage={this.state.griddlePage}
				externalMaxPage={maxPage}
				externalSortAscending={this.state.sortAscending}
				externalSortColumn={this.state.sortColumn}
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

	public UNSAFE_componentWillReceiveProps(nextProps: Props) {
		if (this.props.thesesList !== nextProps.thesesList) {
			// Invalidate caches
			this.filterCache.clear();
			this.sortCache.clear();
		}
	}

	private dataForGriddle(data: Thesis[]): GriddleThesisData[] {
		return toGriddleData(data.slice(0, this.state.griddlePage * THESES_PER_PAGE));
	}

	private getData(): Thesis[] {
		console.time("getData");
		console.time("filter");
		const filteredData = this.filterData(this.props.thesesList);
		console.timeEnd("filter");
		console.time("sort");
		const sortedData = this.sortData(filteredData);
		console.timeEnd("sort");
		console.timeEnd("getData");
		return sortedData;
	}

	private filterData(data: Thesis[]) {
		const advisor = this.state.advisorFilter.toLowerCase();
		const title = this.state.titleFilter.toLowerCase();
		const type = this.state.typeFilter;

		const cacheKey = `${advisor}_${title}_${type}`;
		const cached = this.filterCache.get(cacheKey);
		if (cached) { return cached; }

		const r = data.filter(thesis => (
			thesisMatchesType(thesis, type) &&
			personNameFilter(thesis.advisor, advisor) &&
			thesis.title.toLowerCase().includes(title)
		));
		this.filterCache.set(cacheKey, r);
		return r;
	}

	private sortData(data: Thesis[]): Thesis[] {
		if (!this.state.sortColumn) {
			return data;
		}

		const cacheKey = `${this.state.sortColumn}_${this.state.sortAscending}`;
		const cached = this.sortCache.get(cacheKey);
		if (cached) { return cached; }

		const getter = (
			this.state.sortColumn === "advisorName"
			? (t: Thesis) => t.advisor != null ? t.advisor.displayName : ""
			: (t: Thesis) => t.title
		);
		const adapt = this.state.sortAscending ? (r: number) => r	: (r: number) => -r;

		const r = data.sort((t1: Thesis, t2: Thesis) => (
			adapt(strcmp(getter(t1), getter(t2)))
		));
		this.sortCache.set(cacheKey, r);
		return r;
	}

	private setPage = (pageNum: number) => {
		console.error("Setting page", pageNum);
		this.setState({ griddlePage: pageNum });
	}

	private changeSort = (sortColumn: "title" | "advisorName", asc: boolean) => {
		if (this.state.sortColumn === sortColumn && asc) {
			this.setState({ sortColumn: "" });
		} else {
			this.setState({ sortColumn, sortAscending: asc });
		}
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

	private onTypeFilterChanged = async (newFilter: ThesisTypeFilter) => {
		this.setState({ typeFilter: newFilter });
	}

	private onAdvisorFilterChanged = async (newAdvisorFilter: string) => {
		if (!newAdvisorFilter.trim()) {
			newAdvisorFilter = "";
		}
		this.setState({ advisorFilter: newAdvisorFilter });
	}

	private onTitleFilterChanged = async (newTitleFilter: string) => {
		if (!newTitleFilter.trim()) {
			newTitleFilter = "";
		}
		this.setState({ titleFilter: newTitleFilter });
	}

	private uninstallKeyHandler() {
		Mousetrap.unbind(["up", "down"]);
	}

	private installKeyHandler() {
		Mousetrap.bind("up", this.upArrow);
		Mousetrap.bind("down", this.downArrow);
	}

	private allowArrowSwitch(): boolean {
		return (
			document.activeElement === document.body &&
			!this.props.isEditingThesis
		);
	}

	private upArrow = (e: ExtendedKeyboardEvent) => {
		if (!this.allowArrowSwitch()) {
			return;
		}
		console.warn("previous", e);
	}

	private downArrow = (e: ExtendedKeyboardEvent) => {
		if (!this.allowArrowSwitch()) {
			return;
		}
		console.warn("next", e);
	}
}

function toGriddleData(list: Thesis[]): GriddleThesisData[] {
	return list.map(thesis => ({
		id: thesis.id,
		reserved: thesis.reserved,
		title: thesis.title,
		advisorName: thesis.advisor ? thesis.advisor.displayName : "<brak>",
	}));
}

// nameFilt - already lowercase
function personNameFilter(p: BasePerson | null, nameFilt: string): boolean {
	return p != null && p.displayName.toLowerCase().includes(nameFilt);
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
