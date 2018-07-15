import * as React from "react";
import { ThesesList } from "./ThesesList";
import { Thesis } from "../types";
import { getThesesList, ThesisTypeFilter } from "../backend_callers";
import { awaitSleep } from "common/utils";
import { ThesisDetails } from "./ThesisDetails";

type State = {
	thesesList: Thesis[],
	currentlySelectedThesis: Thesis | null,
};

export class ThesesApp extends React.Component<{}, State> {
	public constructor(props: {}) {
		super(props);
		this.state = {
			thesesList: [],
			currentlySelectedThesis: null,
		};
		this.initList();
	}

	private async initList(): Promise<void> {
		const theses = await getThesesList(ThesisTypeFilter.Default);
		// await awaitSleep(3000);
		this.setState({ thesesList: theses });
	}

	public render() {
		const result = [
			<h2 key="title">Prace dyplomowe</h2>,
			<hr key="divider"/>,
			<div key="container" style={{ margin: "0 auto" }}>
				<ThesesList
					thesesList={this.state.thesesList}
					thesisClickCallback={this.onThesisSelected}
				/>
			</div>
		];
		if (this.state.currentlySelectedThesis) {
			result.push(
				<br key="spacer" />,
				<hr key="divider2" />,
				<ThesisDetails
					key="thesis_details"
					thesis={this.state.currentlySelectedThesis}
				/>
			);
		}

		return result;
	}

	private onThesisSelected = (thesis: Thesis): void => {
		console.warn("Selected", thesis.title);
		this.setState({ currentlySelectedThesis: thesis });
	}
}
