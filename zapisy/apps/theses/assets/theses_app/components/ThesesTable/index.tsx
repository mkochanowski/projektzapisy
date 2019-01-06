/**
 * @file Renders the table view of all theses
 */
import * as React from "react";
import * as Mousetrap from "mousetrap";
import {
	Column, Table, CellMeasurer, CellMeasurerCache,
	AutoSizer, SortDirectionType, SortDirection as RVSortDirection,
	RowMouseEventHandlerParams, TableCellProps,
	InfiniteLoader,
} from "react-virtualized";
import "react-virtualized/styles.css"; // only needs to be imported once

import { ApplicationState, SortColumn, SortDirection } from "../../app_types";
import { ReservationIndicator } from "./ReservationIndicator";
import "./style.less";
import { getDisabledStyle } from "../../utils";
import { LoadingIndicator } from "./LoadingIndicator";
import { NoResultsMessage } from "./NoResultsMessage";
import { UnconstrainedFunction } from "common/types";
import { LoadMode } from "../../theses_logic";
import { inRange } from "common/utils";
import { Thesis } from "../../thesis";

/*
	The theses table is powered by react-virtualized's Table component;
	the docs are very good and available at
	https://github.com/bvaughn/react-virtualized/blob/master/docs/Table.md.
	The following pages are also of interest:
	https://github.com/bvaughn/react-virtualized/blob/master/docs/Column.md#cellrenderer
	(for the column components used inside the table)
	https://github.com/bvaughn/react-virtualized/blob/master/docs/CellMeasurer.md
	(for the "cell measurer" HOC, responsible for dynamically adjusting the height
	of each row to fit the contents)
	https://github.com/bvaughn/react-virtualized/blob/master/docs/InfiniteLoader.md
	(for the infinite scrolling HOC; lets us know when the user has scrolled far
	enough so that we can fetch more rows)
*/

// How close to the end the user has to get before we fetch more
const LOAD_THRESHOLD = 40;

const TABLE_HEIGHT = 300;
const TABLE_CELL_MIN_HEIGHT = 30;
const RESERVED_COLUMN_WIDTH = 150;
const TITLE_COLUMN_WIDTH = 500;
const ADVISOR_COLUMN_WIDTH = 500;

const rowHeightCache = new CellMeasurerCache({
	fixedWidth: true,
	minHeight: TABLE_CELL_MIN_HEIGHT,
});

type Props = {
	applicationState: ApplicationState;
	theses: Thesis[];
	/** The index in the `theses` list of the currently selected thesis */
	selectedIdx: number;
	/** Has the user made any changes? */
	isEditingThesis: boolean;
	sortColumn: SortColumn;
	sortDirection: SortDirection;
	totalThesesCount: number;

	/* Function to be called to switch to the thesis at the specified offset */
	onThesisSelected: (t: Thesis) => void;
	onSortChanged: (column: SortColumn, dir: SortDirection) => void;
	loadMoreRows: (startIndex: number, stopIndex: number) => Promise<void>;
};

export class ThesesTable extends React.PureComponent<Props> {
	/**
	 * Has the user scrolled since the last change of thesis?
	 * Based on this info we know whether or not to focus the table
	 * on the selected thesis - see render() -> scrollToIndex
	 */
	private hasScrolledSinceChange: boolean = false;
	private titleRenderer = this.getCellRenderer(t => t.title);
	private advisorRenderer = this.getCellRenderer(t => t.advisor ? t.advisor.displayName : "<brak>");
	private loaderInstance?: InfiniteLoader;

	componentDidMount() {
		this.installKeyHandler();
	}

	componentWillUnmount() {
		this.uninstallKeyHandler();
	}

	public onListDidChange(mode: LoadMode) {
		// https://github.com/bvaughn/react-virtualized/blob/master/docs/InfiniteLoader.md
		// resetLoadMoreRowsCache - we need to call it if the list changes completely
		// so that it knows to clear its internal caches
		if (this.loaderInstance) {
			this.loaderInstance.resetLoadMoreRowsCache();
		}
		// as above - tell the row height calculator that its caches are no longer
		// valid
		rowHeightCache.clearAll();
		// if the list changed completely, the old position is no longer meaningful,
		// so return to the top
		if (mode === LoadMode.Replace) {
			this.hasScrolledSinceChange = false;
		}
	}

	private isRowLoaded = (index: number) => {
		return index < this.props.theses.length;
	}

	private setLoaderInstance = (loader: InfiniteLoader) => {
		this.loaderInstance = loader;
	}

	public render() {
		const { applicationState } = this.props;
		if (applicationState === ApplicationState.FirstLoad) {
			return <LoadingIndicator/>;
		}
		// Don't let people use the table while something is happening
		const allowInteraction = [
			ApplicationState.Normal, ApplicationState.LoadingMore
		].includes(applicationState);
		return <InfiniteLoader
				loadMoreRows={({ startIndex, stopIndex }) => this.props.loadMoreRows(startIndex, stopIndex)}
				isRowLoaded={({ index }) => this.isRowLoaded(index)}
				rowCount={this.props.totalThesesCount}
				ref={this.setLoaderInstance}
				threshold={LOAD_THRESHOLD}
			>
			{({ onRowsRendered, registerChild }) => (
				// HOC needed for dynamic row heights to accomodate long titles
				<AutoSizer
					disableHeight
					style={allowInteraction ? {} : getDisabledStyle() }
				>
					{({ width }) => this.renderTableItself(width, onRowsRendered, registerChild)}
				</AutoSizer>
			)}
		</InfiniteLoader>;
	}

	/**
	 * Render the Table component only; the render method also has to enclose
	 * it in two HOCs
	 */
	private renderTableItself(
		width: number, onRowsRendered: UnconstrainedFunction, registerChild: UnconstrainedFunction,
	) {
		const { theses, selectedIdx } = this.props;
		const actualIdx = selectedIdx !== -1 ? selectedIdx : 0;
		return <Table
				onRowsRendered={onRowsRendered}
				ref={registerChild}
				rowGetter={this.getRowByIndex}
				rowCount={theses.length}
				rowHeight={rowHeightCache.rowHeight}
				width={width}
				height={TABLE_HEIGHT}
				headerHeight={TABLE_CELL_MIN_HEIGHT}
				sort={this.changeSort}
				sortBy={ownToRvColumn(this.props.sortColumn)}
				sortDirection={ownToRvDirection(this.props.sortDirection)}
				onRowClick={this.onRowClick}
				rowClassName={this.getRowClassName}
				// if the user has initiated scrolling, we no longer specify this
				// otherwise the list would keep jumping to that thesis, preventing
				// scrolling altogether
				scrollToIndex={this.hasScrolledSinceChange ? undefined : actualIdx}
				deferredMeasurementCache={rowHeightCache}
				onScroll={this.onScroll}
				noRowsRenderer={NoResultsMessage}
			>
				<Column
					label="Rezerwacja"
					dataKey="reserved"
					width={RESERVED_COLUMN_WIDTH}
					disableSort
					cellRenderer={ReservationIndicator}
					className={"reservation_cell"}
				/>
				<Column
					label="Tytuł"
					dataKey="title"
					width={TITLE_COLUMN_WIDTH}
					cellRenderer={this.titleRenderer}
				/>
				<Column
					label="Promotor"
					dataKey="advisor"
					width={ADVISOR_COLUMN_WIDTH}
					cellRenderer={this.advisorRenderer}
				/>
		</Table>;
	}

	/**
	 * Return a cell renderer using the provided thesis data getter
	 * This function exists to abstract away the usage of CellMeasurer
	 * @param dataGetter Responsible for converting a Thesis instance to a value to display
	 */
	private getCellRenderer(dataGetter: (t: Thesis) => string) {
		return ({ dataKey, parent, rowIndex, rowData }: TableCellProps) => {
			return (
				<CellMeasurer
					cache={rowHeightCache}
					columnIndex={0}
					key={dataKey}
					parent={parent}
					rowIndex={rowIndex}>
					<div style={{ whiteSpace: "normal" }}>
						{dataGetter(rowData as Thesis)}
					</div>
				</CellMeasurer>
			);
		};
	}

	private getRowByIndex = ({ index }: { index: number}) => {
		return this.props.theses[index];
	}

	/**
	 * Get the CSS class name for the given row; used to implement
	 * alternating colors
	 */
	private getRowClassName = ({ index }: {index: number}) => {
		if (index < 0) {
			return "";
		}
		const colorComponent = `alternating_color_${index % 2 ? "odd" : "even"}`;
		return this.props.selectedIdx === index
			? `active_row ${colorComponent}`
			: colorComponent;
	}

	private onScroll = () => {
		this.hasScrolledSinceChange = true;
	}

	// When the component is re-rendered with new props, some local changes
	// need to be performed
	public UNSAFE_componentWillReceiveProps(nextProps: Props) {
		if (this.props.selectedIdx !== nextProps.selectedIdx) {
			// If the position of the selected thesis in the list changes
			// we should focus the table on it
			this.hasScrolledSinceChange = false;
		}
	}

	private changeSort = (info: { sortBy: string; sortDirection: SortDirectionType }) => {
		// theoretically someone could click this while infinite scroll is loading
		if (this.props.applicationState === ApplicationState.LoadingMore) {
			return;
		}
		const {
			sortColumn: prevSortColumn,
			sortDirection: prevSortDirection
		} = this.props;

		// If list was sorted desc by this column,
		// rather than switch to ASC, return to "natural" order (i.e. no sort)
		if (prevSortColumn === rvColumnToOwn(info.sortBy) && prevSortDirection === SortDirection.Desc) {
			this.props.onSortChanged(SortColumn.None, SortDirection.Asc);
		} else {
			this.props.onSortChanged(
				rvColumnToOwn(info.sortBy),
				rvDirectionToOwn(info.sortDirection)
			);
		}
	}

	private onRowClick = (info: RowMouseEventHandlerParams) => {
		// The typings are invalid and think rowData is some object,
		// hence the ugly cast
		const thesis = info.rowData as any as Thesis;
		this.props.onThesisSelected(thesis);
	}

	private uninstallKeyHandler() {
		Mousetrap.unbind(["up", "down"]);
	}

	private installKeyHandler() {
		Mousetrap.bind("up", this.upArrow);
		Mousetrap.bind("down", this.downArrow);
	}

	private shouldAllowArrowSwitch(): boolean {
		return (
			!this.props.isEditingThesis &&
			this.props.selectedIdx != null
		);
	}

	/** Handle an arrow switch event */
	private arrowSwitch(offset: -1 | 1, e: ExtendedKeyboardEvent) {
		if (!this.shouldAllowArrowSwitch()) {
			return;
		}
		const { selectedIdx, theses } = this.props;
		// If nothing is selected, select the first thesis
		const target = selectedIdx !== -1 ? selectedIdx + offset : 0;
		if (!inRange(target, 0, theses.length - 1)) {
			return;
		}
		this.props.onThesisSelected(theses[target]);
		e.preventDefault();
	}

	private upArrow = (e: ExtendedKeyboardEvent) => {
		this.arrowSwitch(-1, e);
	}

	private downArrow = (e: ExtendedKeyboardEvent) => {
		this.arrowSwitch(+1, e);
	}
}

/**
 * convert react-virtualized's sort column to our enum
 */
function rvColumnToOwn(sortColumn: string) {
	switch (sortColumn) {
		case "advisor": return SortColumn.Advisor;
		case "title": return SortColumn.Title;
		default: return SortColumn.None;
	}
}
/**
 * convert react-virtualized's sort direction to our enum
 */
function rvDirectionToOwn(sortDirection: SortDirectionType) {
	switch (sortDirection) {
		case RVSortDirection.ASC: return SortDirection.Asc;
		case RVSortDirection.DESC: return SortDirection.Desc;
	}
}

/**
 * convert our sort column to react-virtualized's format
 */
function ownToRvColumn(sortColumn: SortColumn) {
	switch (sortColumn) {
		case SortColumn.Advisor: return "advisor";
		case SortColumn.Title: return "title";
		case SortColumn.None: return "";
	}
}
/**
 * convert our sort direction to react-virtualized's format
 */
function ownToRvDirection(sortDirection: SortDirection) {
	switch (sortDirection) {
		case SortDirection.Asc: return RVSortDirection.ASC;
		case SortDirection.Desc: return RVSortDirection.DESC;
	}
}
