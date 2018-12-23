import * as React from "react";
import * as Mousetrap from "mousetrap";
import {
	Column, Table, CellMeasurer, CellMeasurerCache,
	AutoSizer, SortDirectionType, SortDirection as RVSortDirection,
	RowMouseEventHandlerParams, TableCellProps,
} from "react-virtualized";
import "react-virtualized/styles.css"; // only needs to be imported once

import { Thesis } from "../../types";
import { ApplicationState } from "../../types/misc";
import { ReservationIndicator } from "./ReservationIndicator";
import "./style.less";
import { getDisabledStyle } from "../../utils";
import { LoadingIndicator } from "./LoadingIndicator";
import { SortColumn, SortDirection } from "../theses_store";

const TABLE_HEIGHT = 300;
const TABLE_CELL_MIN_HEIGHT = 30;

const rowHeightCache = new CellMeasurerCache({
	fixedWidth: true,
	minHeight: TABLE_CELL_MIN_HEIGHT,
});

type Props = {
	applicationState: ApplicationState;
	theses: Thesis[];
	selectedIdx: number | null;
	isEditingThesis: boolean;
	sortColumn: SortColumn;
	sortDirection: SortDirection;

	switchToThesisWithOffset: (offset: number) => void;
	onThesisSelected: (t: Thesis) => void;
	onSortChanged: (column: SortColumn, dir: SortDirection) => void;
};

const initialState = {
	hasScrolled: false,
};
type State = typeof initialState;

export class ThesesTable extends React.PureComponent<Props, State> {
	state = initialState;

	private titleRenderer = this.getCellRenderer(t => t.title);
	private advisorRenderer = this.getCellRenderer(t => t.advisor ? t.advisor.displayName : "<brak>");

	componentDidMount() {
		this.installKeyHandler();
	}

	componentWillUnmount() {
		this.uninstallKeyHandler();
	}

	public render() {
		if (this.props.applicationState === ApplicationState.InitialLoading) {
			return <LoadingIndicator/>;
		}
		const { theses, selectedIdx } = this.props;
		const shouldDisable = this.props.applicationState === ApplicationState.PerformingBackendChanges;
		return <AutoSizer
			disableHeight
			style={shouldDisable ? getDisabledStyle() : {}}
		>
			{({ width }) => (
				<Table
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
					scrollToIndex={!this.state.hasScrolled && selectedIdx !== null ? selectedIdx : undefined}
					deferredMeasurementCache={rowHeightCache}
					onScroll={this.onScroll}
				>
					<Column
						label="Rezerwacja"
						dataKey="reserved"
						width={150}
						disableSort
						cellRenderer={ReservationIndicator}
						className={"reservation_cell"}
					/>
					<Column
						label="Tytuł"
						dataKey="title"
						width={500}
						cellRenderer={this.titleRenderer}
					/>
					<Column
						label="Promotor"
						dataKey="advisor"
						width={500}
						cellRenderer={this.advisorRenderer}
					/>
				</Table>
		)	}
		</AutoSizer>;
	}

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
		this.setState({ hasScrolled: true });
	}

	public UNSAFE_componentWillReceiveProps(nextProps: Props) {
		if (this.props.theses !== nextProps.theses) {
			this.onListChanged();
		} else if (this.props.selectedIdx !== nextProps.selectedIdx) {
			this.setState({ hasScrolled: false });
		}
	}

	// If the displayed list changes logically (contents, order)
	// there are some caches to invalidate
	private onListChanged() {
		rowHeightCache.clearAll();
	}

	private changeSort = (info: { sortBy: string; sortDirection: SortDirectionType }) => {
		const {
			sortColumn: prevSortColumn,
			sortDirection: prevSortDirection
		} = this.props;

		// If list was sorted DESC by this column.
		// Rather than switch to ASC, return to "natural" order.
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
		// The typings are invalid and think rowData is some object
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

	private allowArrowSwitch(): boolean {
		return (
			!this.props.isEditingThesis &&
			this.props.selectedIdx != null
		);
	}

	private arrowSwitch(offset: -1 | 1, e: ExtendedKeyboardEvent) {
		if (!this.allowArrowSwitch()) {
			return;
		}
		this.props.switchToThesisWithOffset(offset);
		e.preventDefault();
	}

	private upArrow = (e: ExtendedKeyboardEvent) => {
		this.arrowSwitch(-1, e);
	}

	private downArrow = (e: ExtendedKeyboardEvent) => {
		this.arrowSwitch(+1, e);
	}
}

// react-virtualized's sort column to our enum
function rvColumnToOwn(sortColumn: string) {
	switch (sortColumn) {
		case "advisor": return SortColumn.Advisor;
		case "title": return SortColumn.Title;
		default: return SortColumn.None;
	}
}
// react-virtualized's sort direction to our enum
function rvDirectionToOwn(sortDirection: SortDirectionType) {
	switch (sortDirection) {
		case RVSortDirection.ASC: return SortDirection.Asc;
		case RVSortDirection.DESC: return SortDirection.Desc;
	}
}

// as above, but reverse
function ownToRvColumn(sortColumn: SortColumn) {
	switch (sortColumn) {
		case SortColumn.Advisor: return "advisor";
		case SortColumn.Title: return "title";
		case SortColumn.None: return "";
	}
}
function ownToRvDirection(sortDirection: SortDirection) {
	switch (sortDirection) {
		case SortDirection.Asc: return RVSortDirection.ASC;
		case SortDirection.Desc: return RVSortDirection.DESC;
	}
}
