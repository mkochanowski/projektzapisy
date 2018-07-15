import * as React from "react";
import { Thesis } from "../../types";
import { ThesisTopRow } from "./ThesisTopRow";

type Props = {
	thesis: Thesis,
};

export class ThesisDetails extends React.Component<Props> {
	public render() {
		return <div style= {{
			border: "1px solid black",
			padding: "15px",
		}}>
			<ThesisTopRow
				thesis={this.props.thesis}
			/>
		</div>;
	}
}
