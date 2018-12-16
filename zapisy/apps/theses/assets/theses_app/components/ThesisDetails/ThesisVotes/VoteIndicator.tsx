import * as React from "react";
import styled from "styled-components";

import { ThesisVote } from "../../../types";

type Props = {
	value: ThesisVote;
	active: boolean;
};

export function VoteIndicator(props: Props) {
	const Component = props.active ? Container : DisabledContainer;
	return <Component>{indicatorForValue(props.value)}</Component>;
}

function indicatorForValue(value: ThesisVote) {
	switch (value) {
		case ThesisVote.None: return "\u{2B1C}";
		case ThesisVote.Accepted: return "\u{2705}";
		case ThesisVote.Rejected: return "\u{274C}";
		case ThesisVote.UserMissing: return "\u{2753}";
	}
}

const Container = styled.span`
	width: 18px;
	display: inline-block;
`;

const DisabledContainer = Container.extend`
	filter: grayscale(30%) opacity(0.6);
`;
