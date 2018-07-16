import * as React from "react";
import styled from "styled-components";

import { Thesis } from "../../types";
import { ThesisTopRow } from "./ThesisTopRow";
import { ThesisMiddleForm } from "./ThesisMiddleForm";
import { ThesisVotes } from "./ThesisVotes";

type Props = {
	thesis: Thesis,
};

const SaveButton = styled.button`
	height: 30px;
	border: 1px solid black;
	background: white;

	&:focus {
		border: 2px solid black;
		font-weight: bold;
	}
`;

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
				<SaveButton>Zapisz</SaveButton>
			</div>
		</div>;
	}
}
