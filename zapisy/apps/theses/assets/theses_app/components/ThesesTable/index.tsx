import * as React from "react";
import * as Mousetrap from "mousetrap";
import {
	Column, Table, TableCellDataGetterParams,
	AutoSizer, SortDirectionType, SortDirection, RowMouseEventHandlerParams,
} from "react-virtualized";
import "react-virtualized/styles.css"; // only needs to be imported once

import { ThesisTypeFilter } from "../../backend_callers";
import { Thesis, ThesisStatus, ThesisKind, BasePerson } from "../../types";
import { ApplicationState } from "../../types/application_state";
import { TopFilters } from "./TopFilters";
import { strcmp, inRange } from "common/utils";
import { ReservationIndicator } from "./ReservationIndicator";
import "./style.less";

type Props = {
	applicationState: ApplicationState;
	thesesList: Thesis[];
	isEditingThesis: boolean;
	selectedThesis: Thesis | null;

	thesisForId: (id: number) => Thesis | null;
	onThesisClicked: (t: Thesis) => void;
};

const initialState = {
	typeFilter: ThesisTypeFilter.Default,
	titleFilter: "",
	advisorFilter: "",
	griddlePage: 1,
	sortDirection: SortDirection.ASC as SortDirectionType,
	sortColumn: "" as ("title" | "advisor" | ""),
	// cache this since finding it isn't a zero cost operation
	currentThesisIdx: -1,
};
type State = typeof initialState;

export class ThesesTable extends React.PureComponent<Props, State> {
	state = initialState;
	private tableData: Thesis[] | null = null;
	private filterCache: Map<string, Thesis[]> = new Map();

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

	private renderThesesList() {
		const data = this.getData();
		const scrollTo = this.state.currentThesisIdx !== -1
			? this.state.currentThesisIdx
			: undefined;
		return <AutoSizer disableHeight>
			{({ width }) => (
				<Table
					rowGetter={this.getRowByIndex}
					rowCount={data.length}
					rowHeight={30}
					width={width}
					height={200}
					headerHeight={30}
					sort={this.changeSort}
					sortBy={this.state.sortColumn}
					sortDirection={this.state.sortDirection}
					onRowClick={this.onRowClick}
					rowClassName={this.getRowClassName}
					scrollToIndex={scrollTo}
				>
					<Column
						label="Rezerwacja"
						dataKey="reserved"
						width={150}
						disableSort
						cellRenderer={ReservationIndicator}
					/>
					<Column
						label="Tytuł"
						dataKey="title"
						width={500}
						cellDataGetter={getTitle}
					/>
					<Column
						label="Promotor"
						dataKey="advisor"
						width={500}
						cellDataGetter={getAdvisor}
					/>
				</Table>
		)	}
		</AutoSizer>;
	}

	private getRowByIndex = ({ index }: { index: number}) => {
		return this.getData()[index];
	}

	private getRowClassName = ({ index }: {index: number}) => {
		if (index < 0) {
			return "";
		}
		const colorComponent = `alternating_color_${index % 2 ? "odd" : "even"}`;
		return this.state.currentThesisIdx === index
			? `active_row ${colorComponent}`
			: colorComponent;
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
			this.resetAllCaches();
		}
		if (nextProps.selectedThesis) {
			this.setState({
				currentThesisIdx: this.getThesisIdx(nextProps.selectedThesis),
			});
		}
	}

	private getThesisIdx(thesis: Thesis) {
		return this.getData().findIndex(thesis.isEqual);
	}

	private resetAllCaches() {
		this.resetFilterCache();
		this.resetData();
	}

	private resetData(): void {
		this.tableData = null;
	}

	private getData(): Thesis[] {
		if (this.tableData) {
			return this.tableData;
		}
		const filteredData = this.filterData(this.props.thesesList);
		const sortedData = this.sortData(filteredData);
		return this.tableData = sortedData;
	}

	private resetFilterCache() {
		this.filterCache.clear();
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

		const getter = (
			this.state.sortColumn === "advisor"
			? (t: Thesis) => t.advisor != null ? t.advisor.displayName : ""
			: (t: Thesis) => t.title
		);
		const adapt = this.state.sortDirection === SortDirection.ASC
			? (r: number) => r : (r: number) => -r;

		return data.slice().sort((t1: Thesis, t2: Thesis) => (
			adapt(strcmp(getter(t1), getter(t2)))
		));
	}

	private changeSort = (info: { sortBy: string; sortDirection: SortDirectionType }) => {
		this.resetData();
		this.setState({ sortColumn: info.sortBy as any, sortDirection: info.sortDirection });
	}

	private onRowClick = (info: RowMouseEventHandlerParams) => {
		// The typings are invalid and think rowData is some object
		const thesis = info.rowData as any as Thesis;
		this.props.onThesisClicked(thesis);
	}

	private onTypeFilterChanged = (newFilter: ThesisTypeFilter) => {
		this.setState({ typeFilter: newFilter });
		this.resetData();
	}

	private onAdvisorFilterChanged = (newAdvisorFilter: string) => {
		if (!newAdvisorFilter.trim()) {
			newAdvisorFilter = "";
		}
		this.setState({ advisorFilter: newAdvisorFilter });
		this.resetData();
	}

	private onTitleFilterChanged = (newTitleFilter: string) => {
		if (!newTitleFilter.trim()) {
			newTitleFilter = "";
		}
		this.setState({ titleFilter: newTitleFilter });
		this.resetData();
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
			!this.props.isEditingThesis &&
			this.props.selectedThesis != null
		);
	}

	private arrowSwitch(offset: -1 | 1, e: ExtendedKeyboardEvent) {
		if (!this.allowArrowSwitch()) { return;	}
		const data = this.getData();
		const target = this.state.currentThesisIdx + offset;
		if (!inRange(target, 0, data.length - 1)) { return; }
		this.props.onThesisClicked(data[target]);
		e.preventDefault();
	}

	private upArrow = (e: ExtendedKeyboardEvent) => {
		this.arrowSwitch(-1, e);
	}

	private downArrow = (e: ExtendedKeyboardEvent) => {
		this.arrowSwitch(+1, e);
	}
}

function getTitle(params: TableCellDataGetterParams) {
	const thesis = params.rowData as Thesis;
	return thesis.title;
}

function getAdvisor(params: TableCellDataGetterParams) {
	const thesis = params.rowData as Thesis;
	return thesis.advisor ? thesis.advisor.displayName : "<brak>";
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
