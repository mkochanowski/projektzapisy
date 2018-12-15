import * as React from "react";

import { Employee, Thesis, ThesisVote } from "../../../types";
import { SingleVote } from "./SingleVote";
import styled from "styled-components";

type Props = {
	thesis: Thesis,
	thesesBoard: Employee[],
	onChange: (member: Employee, newValue: ThesisVote) => void;
};

export function ThesisVotes(props: Props) {
	const votes = props.thesesBoard.map((emp, i) => (
		<SingleVote
			key={i}
			voter={emp}
			value={props.thesis.votes[emp.id] || ThesisVote.None}
			onChange={nv => props.onChange(emp, nv)}
		/>
	));
	return <VotesContainer>
		<Header>Głosy</Header>
		{votes}
	</VotesContainer>;
}

const Header = styled.div`
	font-weight: bold;
	font-size: 16px;
	color: black;
	margin-bottom: 15px;
`;

const VotesContainer = styled.div`
	text-align: center;
	width: 100%;
`;
