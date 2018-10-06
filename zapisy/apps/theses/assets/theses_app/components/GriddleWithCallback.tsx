import * as React from "react";
import { isEmpty } from "lodash";
import Griddle, { GriddleProps } from "griddle-react";
import { Omit } from "common/utils";

type State<T> = {
	results: T[];
	page: number;
	maxPage: number;
	totalResults: number;
	sortColumn: string | undefined;
	sortAscending: boolean;
	isLoading: boolean;
};

export type ExternalResults<T> = {
	results: T[];
	totalResults: number;
};

type Props<T> =
	GriddleProps<T> &
	Omit<GriddleProps<T>, "externalLoadingComponent"> &
	{
		getExternalResults: (
			filterColumn: string | undefined, sortAsc: boolean,
			page: number, callback: (s: ExternalResults<T>) => void,
		) => void;
		loadingComponent: React.ComponentType<void>;
		resultsPerPage: number;
		// This isn't any different than the standard Griddle prop but the type
		// definition there is hopelessly broken
		onRowClick?: (row: any, e: MouseEvent) => void;
	};

class GriddleWithCallback<T> extends React.Component<Props<T>, State<T>> {
	constructor(props: Props<T>) {
		super(props);
		this.state = {
			results: [],
			page: 0,
			maxPage: 0,
			totalResults: 0,
			sortColumn: undefined,
			sortAscending: true,
			isLoading: true,
		};
	}

	componentDidMount() {
		if (!this.hasExternalResults()) {
			console.error("When using GriddleWithCallback, a getExternalResults callback must be supplied.");
			return;
		}

		// Update the state with external results when mounting
		this.updateStateWithExternalResults(this.state, updatedState => {
			this.setState(updatedState);
		});
	}

	// componentWillReceiveProps() {
	// 	// Update the state with external results.
	// 	this.updateStateWithExternalResults(this.state, updatedState => {
	// 		this.setState(updatedState);
	// 	});
	// }

	getExternalResults<K extends keyof State<T>>(
		state: Pick<State<T>, K>,
		callback: (updatedState: ExternalResults<T>) => void,
	) {
		let sortColumn;
		let sortAscending;
		let page;

		// Fill the search properties.

		if (state.sortColumn !== undefined) {
			sortColumn = state.sortColumn;
		} else {
			sortColumn = this.state.sortColumn;
		}

		sortColumn = isEmpty(sortColumn) ? this.props.initialSort : sortColumn;

		if (state.sortAscending !== undefined) {
			sortAscending = state.sortAscending;
		} else {
			sortAscending = this.state.sortAscending;
		}

		if (state.page !== undefined) {
			page = state.page;
		} else {
			page = this.state.page;
		}

		// Obtain the results
		this.props.getExternalResults(
			sortColumn, sortAscending, page, callback,
		);
	}

	updateStateWithExternalResults<K extends keyof State<T>>(
		state: Pick<State<T>, K>,
		callback: (updatedState: Pick<State<T>, K>) => void,
	) {
		// Update the table to indicate that it's loading.
		this.setState({ isLoading: true });
		// Grab the results.
		this.getExternalResults(state, externalResults => {
			// Fill the state result properties
			if (this.props.enableInfiniteScroll &&
				this.state.results &&
				state.page > this.state.page
			) {
				state.results = this.state.results.concat(externalResults.results);
			} else {
				state.results = externalResults.results;
			}

			state.totalResults = externalResults.totalResults;
			state.maxPage = this.getMaxPage(this.props.resultsPerPage, externalResults.totalResults);
			state.isLoading = false;

			// If the current page is larger than the max page, reset the page.
			if (state.page >= state.maxPage) {
				state.page = state.maxPage - 1;
			}

			callback(state);
		});
	}

	getMaxPage(pageSize: number, totalResults?: number) {
		if (!totalResults) {
			totalResults = this.state.totalResults;
		}

		return Math.ceil(totalResults / pageSize);
	}

	hasExternalResults() {
		return typeof(this.props.getExternalResults) === "function";
	}

	changeSort = (sortColumn: string, sortAscending: boolean) => {
		// this should change the sort for the given column
		const state = {
			page: 0,
			sortColumn: sortColumn,
			sortAscending: sortAscending
		};

		this.updateStateWithExternalResults(state, updatedState => {
			this.setState(updatedState);
		});
	}

	setPage = (index: number) => {
		// This should interact with the data source to get the page at the given index
		const state = {
			page: index,
		};

		this.updateStateWithExternalResults(state, updatedState => {
			this.setState(updatedState);
		});
	}

	render() {
		return <Griddle {...this.props} useExternal={true} externalSetPage={this.setPage}
			externalChangeSort={this.changeSort}
			externalSetPageSize={() => ({})} externalMaxPage={this.state.maxPage}
			externalSetFilter={() => ({})}
			externalCurrentPage={this.state.page}
			results={this.state.results} tableClassName="table" resultsPerPage={this.props.resultsPerPage}
			externalSortColumn={this.state.sortColumn} externalSortAscending={this.state.sortAscending}
			externalLoadingComponent={this.props.loadingComponent} externalIsLoading={this.state.isLoading}
		/>;
	}
}

export { GriddleWithCallback };
