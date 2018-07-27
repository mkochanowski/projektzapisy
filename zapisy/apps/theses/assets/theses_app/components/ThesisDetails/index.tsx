import * as React from "react";
import Button from "react-button-component";
import styled from "styled-components";
import { clone } from "lodash";

import { Thesis, ThesisStatus } from "../../types";
import { ThesisTopRow } from "./ThesisTopRow";
import { ThesisMiddleForm } from "./ThesisMiddleForm";
import { ThesisVotes } from "./ThesisVotes";

const MainDetailsContainer = styled.div`
border: 1px solid black;
padding: 15px;
display: flex;
flex-direction: row;
`;

const LeftDetailsContainer = styled.div`
width: 100%;
`;

const RightDetailsContainer = styled.div`
display: flex;
flex-direction: column;
justify-content: space-between;
margin-left: 20px;
`;

type Props = {
	selectedThesis: Thesis,
};

type State = {
	currentThesis: Thesis;
};

export class ThesisDetails extends React.Component<Props, State> {
	public constructor(props: Props) {
		super(props);
		this.state = {
			currentThesis: clone(props.selectedThesis)
		};
	}

	public render() {
		return <MainDetailsContainer>
			<LeftDetailsContainer>
				<ThesisTopRow
					thesis={this.state.currentThesis}
				/>
				<ThesisMiddleForm
					thesis={this.state.currentThesis}
				/>
			</LeftDetailsContainer>
			<RightDetailsContainer>
				<ThesisVotes />
				<Button onClick={this.onSaveRequested}>Zapisz</Button>
			</RightDetailsContainer>
		</MainDetailsContainer>;
	}

	private onSaveRequested = () => {
		console.warn("Save clicked");
	}
}
