import * as React from "react";
import update from "immutability-helper";

import { ThesesList } from "./ThesesList";
import { Thesis } from "../types";
import { getThesesList, ThesisTypeFilter, getThesisById } from "../backend_callers";
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
		this.setState({ thesesList: theses, currentlySelectedThesis: theses[0] });
	}

	public render() {
		console.error("Main rerender");
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
					selectedThesis={this.state.currentlySelectedThesis}
					onModifiedThesisSaved={this.onModifiedThesisSaved}
				/>
			);
		}

		return result;
	}

	private onThesisSelected = (thesis: Thesis): void => {
		console.warn("Selected", thesis.title);
		this.setState({ currentlySelectedThesis: thesis });
	}

	private onModifiedThesisSaved = async (): Promise<void> => {
		const currentThesis = this.state.currentlySelectedThesis;
		if (currentThesis === null) {
			throw new Error("Modified thesis was saved but no thesis selected");
		}
		const idx = this.state.thesesList.findIndex(currentThesis.isEqual);
		const updatedInstance = await getThesisById(currentThesis.id);
		console.warn("New thesis to insert at index:", idx, updatedInstance);
		this.setState(update(this.state, { thesesList: { $splice: [[idx, 1, updatedInstance]] } }));
	}
}
