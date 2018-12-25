import * as React from "react";
import styled from "styled-components";

import { ThesisVote } from "../../../types";

type Props = {
	value: ThesisVote;
	active: boolean;
};

export function VoteIndicator(props: Props) {
	const Component = props.active ? Container : DisabledContainer;
	const { text, color = "default" } = paramsForValue(props.value);
	return <Component cssColor={color}>{text}</Component>;
}

function paramsForValue(value: ThesisVote) {
	switch (value) {
		case ThesisVote.None: return { text: "\u{2B1C}" };
		case ThesisVote.Accepted: return { text: "\u{2705}", color: "green" };
		case ThesisVote.Rejected: return { text: "\u{274C}", color: "red" };
		case ThesisVote.UserMissing: return { text: "\u{2753}" };
	}
}

type ContainerProps = { cssColor: string };
const Container = styled.span`
	width: 18px;
	display: inline-block;
	color: ${(props: ContainerProps) => props.cssColor}
`;

const DisabledContainer = styled(Container)`
	filter: grayscale(30%) opacity(0.6);
`;
