import * as React from "react";
import { ThesesList } from "./ThesesList";
import { Thesis } from "../types";
import { getThesesList, ThesisTypeFilter } from "../backend_callers";
import { awaitSleep } from "common/utils";

type State = {
	thesesList: Thesis[],
};

export class ThesesApp extends React.Component<{}, State> {
	public constructor(props: {}) {
		super(props);
		this.state = {
			thesesList: [],
		};
		this.initList();
	}

	private async initList(): Promise<void> {
		const theses = await getThesesList(ThesisTypeFilter.Default);
		// await awaitSleep(3000);
		this.setState({ thesesList: theses });
	}

	public render() {
		return [
			<h2 key="title">Prace dyplomowe</h2>,
			<hr key="divider"/>,
			<div key="container" style={{ margin: "0 auto" }}>
				<ThesesList
					thesesList={this.state.thesesList}
				/>
			</div>
		];
	}
}
