import * as React from "react";
import { ThesisVote, Employee } from "../../../types";
import styled from "styled-components";

type Props = {
	value: ThesisVote;
	voter: Employee;
	onChange: (v: ThesisVote) => void;
};

const voteCycle = [ThesisVote.None, ThesisVote.Accepted, ThesisVote.Rejected];

export function SingleVote(props: Props) {
	return <VoteContainer>
		<VoteIndicatorContainer
			onClick={() => props.onChange(nextValue(props.value))}
		>
			{indicatorForValue(props.value)}
		</VoteIndicatorContainer>
		<VoteLabel>{props.voter.displayName.split(" ")[0]}</VoteLabel>
	</VoteContainer>;
}

function indicatorForValue(value: ThesisVote) {
	switch (value) {
		case ThesisVote.None: return "\u{2B1C}";
		case ThesisVote.Accepted: return "\u{2705}";
		case ThesisVote.Rejected: return "\u{274C}";
		case ThesisVote.UserMissing: return "\u{2753}";
	}
}

function nextValue(value: ThesisVote) {
	const valIdx = voteCycle.indexOf(value);
	return voteCycle[(valIdx + 1) % voteCycle.length];
}

const VoteIndicatorContainer = styled.span`
	user-select: none;
	cursor: pointer;
	width: 18px;
	display: inline-block;
`;

const VoteContainer = styled.div`
	margin-bottom: 5px;
`;

const VoteLabel = styled.span`
	margin-left: 5px;
`;
