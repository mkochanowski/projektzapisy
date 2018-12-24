import * as React from "react";
import styled from "styled-components";

const MessageContainer = styled.div`
	position: relative;
	top: 50%;
	transform: translateY(-50%);
	width: 100%;
	text-align: center;
	font-size: 18px;
`;

export function NoResultsMessage() {
	return <MessageContainer>Brak wyników</MessageContainer>;
}
