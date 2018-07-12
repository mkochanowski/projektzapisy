import * as React from "react";
import ReactTable from "react-table";
import "react-table/react-table.css";
import { ThesesList } from "./ThesesList";
import { Thesis } from "../types";
import { getThesesList, ThesisTypeFilter } from "../backend_callers";

type State = {
	thesesList: Thesis[],
};

export class ThesesApp extends React.Component<{}, State> {
	constructor(props: {}) {
		super(props);
		this.state = {
			thesesList: [],
		};
		this.initList();
	}

	private async initList(): Promise<void> {
		const theses = await getThesesList(ThesisTypeFilter.All);
		this.setState({ thesesList: theses });
	}

	render(): JSX.Element {
		return (
			<div style={{ margin: "0 auto" }}>
				<ThesesList currentThesesList={this.state.thesesList}/>
			</div>
		);
	}
}
