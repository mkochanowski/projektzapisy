import * as React from "react";
import Button from "react-button-component";

import { Thesis } from "../../types";
import { ThesisTopRow } from "./ThesisTopRow";
import { ThesisMiddleForm } from "./ThesisMiddleForm";
import { ThesisVotes } from "./ThesisVotes";

type Props = {
	thesis: Thesis,
};

export class ThesisDetails extends React.Component<Props> {
	public render() {
		return <div style= {{
			border: "1px solid black",
			padding: "15px",
			display: "flex",
			flexDirection: "row"
		}}>
			<div style={{ width: "100%" }}>
				<ThesisTopRow
					thesis={this.props.thesis}
				/>
				<ThesisMiddleForm
					thesis={this.props.thesis}
				/>
			</div>
			<div style={{
				display: "flex",
				flexDirection: "column",
				justifyContent: "space-between",
				marginLeft: "20px"
			}}>
				<ThesisVotes />
				<Button onClick={this.onSaveRequested}>Zapisz</Button>
			</div>
		</div>;
	}

	private onSaveRequested = () => {
		console.warn("Save clicked");
	}
}
