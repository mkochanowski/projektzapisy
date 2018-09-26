import * as React from "react";
import update from "immutability-helper";

import { ThesesList } from "./ThesesList";
import { Thesis } from "../types";
import { getThesesList, ThesisTypeFilter, getThesisById } from "../backend_callers";
import { ThesisDetails } from "./ThesisDetails";
import { ErrorBoundary } from "./ErrorBoundary";

type State = {
	thesesList: Thesis[];
	curThesisIdx: number | null;
};

export class ThesesApp extends React.Component<{}, State> {
	public constructor(props: {}) {
		super(props);
		this.state = {
			thesesList: [],
			curThesisIdx: null,
		};
		this.initList();
	}

	private async initList(): Promise<void> {
		const theses = await getThesesList(ThesisTypeFilter.Default);
		this.setState({ thesesList: theses, curThesisIdx: 0 });
	}

	public render() {
		console.error("Main rerender");
		const result = [
			<div key="container" style={{ margin: "0 auto" }}>
				<ThesesList
					thesesList={this.state.thesesList}
					thesisClickCallback={this.onThesisSelected}
				/>
			</div>
		];
		if (this.state.curThesisIdx !== null) {
			result.push(
				<br key="spacer" />,
				<hr key="divider2" />,
				<ThesisDetails
					key="thesis_details"
					selectedThesis={this.state.thesesList[this.state.curThesisIdx]}
					onModifiedThesisSaved={this.onModifiedThesisSaved}
				/>
			);
		}

		return <ErrorBoundary>{result}</ErrorBoundary>;
	}

	private onThesisSelected = (thesis: Thesis): void => {
		const idx = this.state.thesesList.findIndex(thesis.isEqual);
		if (idx === -1) {
			throw new Error("Selected thesis not found");
		}
		this.setState({ curThesisIdx: idx });
	}

	private onModifiedThesisSaved = async (): Promise<void> => {
		const curIdx = this.state.curThesisIdx;
		if (curIdx === null) {
			throw new Error("Modified thesis was saved but no thesis selected");
		}
		const currentThesis = this.state.thesesList[curIdx];
		const updatedInstance = await getThesisById(currentThesis.id);
		console.warn("New thesis to insert at index:", curIdx, updatedInstance);
		this.setState(update(this.state, { thesesList: { $splice: [[curIdx, 1, updatedInstance]] } }));
	}
}
