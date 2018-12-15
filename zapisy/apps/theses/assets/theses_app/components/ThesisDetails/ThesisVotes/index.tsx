import * as React from "react";

import { Employee, Thesis, ThesisVote } from "../../../types";
import { SingleVote } from "./SingleVote";
import styled from "styled-components";

type Props = {
	thesis: Thesis,
	thesesBoard: Employee[],
};

export function ThesisVotes(props: Props) {
	const votes = props.thesesBoard.map((emp, i) => (
		<SingleVote
			key={i}
			voter={emp}
			value={ThesisVote.None}
		/>
	));
	return <div>
		<Header>Głosy</Header>
		{votes}
	</div>;
}

const Header = styled.div`
	width: 100%;
	text-align: center;
	font-weight: bold;
	font-size: 16px;
	color: black;
	margin-bottom: 15px;
`;
