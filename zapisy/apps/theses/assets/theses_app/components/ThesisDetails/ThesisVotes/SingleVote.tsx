import * as React from "react";
import { ThesisVote, Employee, AppUser } from "../../../types";
import styled from "styled-components";
import { canCastVoteAsUser } from "../../../permissions";
import { VoteIndicator } from "./VoteIndicator";

type Props = {
	user: AppUser;
	value: ThesisVote;
	voter: Employee;
	onChange: (v: ThesisVote) => void;
};

const voteCycle = [ThesisVote.None, ThesisVote.Accepted, ThesisVote.Rejected];

export function SingleVote(props: Props) {
	const allowAction = canCastVoteAsUser(props.user, props.voter);
	const sameUser = props.user.user.isEqual(props.voter);
	const content = <>
		<VoteIndicator active={allowAction} value={props.value} />
		<VoteLabel
			style={sameUser ? { fontWeight: "bold" } : {}}
		>{props.voter.displayName.split(" ")[0]}</VoteLabel>
	</>;
	return allowAction
		? <VoteContainerActive
			onClick={() => props.onChange(nextValue(props.value))}
		>{content}</VoteContainerActive>
		: <VoteContainerInactive>{content}</VoteContainerInactive>;
}

function nextValue(value: ThesisVote) {
	const valIdx = voteCycle.indexOf(value);
	return voteCycle[(valIdx + 1) % voteCycle.length];
}

const VoteContainerBase = styled.div`
	margin-bottom: 5px;
	user-select: none;
`;

const VoteContainerActive = styled(VoteContainerBase)`
	cursor: pointer;
`;

const VoteContainerInactive = styled(VoteContainerBase)`
	cursor: default;
`;

const VoteLabel = styled.span`
	margin-left: 5px;
	width: 60px;
	display: inline-block;
	text-align: left;
`;
