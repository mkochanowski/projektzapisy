import * as React from "react";
import Button from "react-button-component";
import styled from "styled-components";

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
	thesis: Thesis,
};

type State = {
	isReserved: boolean;
	modifiedDate: Date;
	status: ThesisStatus;
	title: string;
	advisorId: number | null;
	auxAdvisorId: number | null;
	studentId: number | null;
	secondStudentId: number | null;
	description: string;
};

export class ThesisDetails extends React.Component<Props, State> {
	public constructor(props: Props) {
		super(props);
		const { thesis } = props;
		this.state = {
			isReserved: thesis.reserved,
			modifiedDate: thesis.modifiedDate,
			status: thesis.status,
			title: thesis.title,
			advisorId: thesis.advisor ? thesis.advisor.id : null,
			auxAdvisorId: thesis.auxiliaryAdvisor ? thesis.auxiliaryAdvisor.id : null,
			studentId: thesis.student ? thesis.student.id : null,
			secondStudentId: thesis.secondStudent ? thesis.secondStudent.id : null,
			description: thesis.description,
		};
	}

	public render() {
		return <MainDetailsContainer>
			<LeftDetailsContainer>
				<ThesisTopRow
					thesis={this.props.thesis}
				/>
				<ThesisMiddleForm
					thesis={this.props.thesis}
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
