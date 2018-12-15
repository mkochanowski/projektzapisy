import * as React from "react";
import Checkbox from "react-three-state-checkbox";
import { ThesisVote, Employee } from "../../../types";
import styled from "styled-components";

type Props = {
	value: ThesisVote;
	voter: Employee;
};

export function SingleVote(props: Props) {
	return <VoteContainer>
		<Checkbox
			checked={props.value === ThesisVote.Accepted}
			indeterminate={props.value === ThesisVote.None}
			// onChange={}
		/>
		<VoteLabel>{props.voter.displayName}</VoteLabel>
	</VoteContainer>;
}

const VoteContainer = styled.div`
	margin-bottom: 5px;
`;

const VoteLabel = styled.span`
	vertical-align: text-bottom;
	margin-left: 5px;
`;
