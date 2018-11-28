import * as React from "react";
import styled from "styled-components";

const ErrorTextContainer = styled.div`
width: 100%;
padding: 40px;
text-align: center;
`;

type Props = {
	errorTitle: JSX.Element;
	errorDescription?: JSX.Element;
};

const DEFAULT_ERROR_DESCRIPTION = (
	"Przeładuj stronę i spróbuj jeszcze raz. " +
	"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów."
);

export function ErrorBox(props: Props) {
	return (
		<ErrorTextContainer>
			<h2>Wystąpił błąd</h2>
			<br />
			<h3>{props.errorTitle}</h3>
			<br />
			<p>{props.errorDescription || DEFAULT_ERROR_DESCRIPTION}</p>
		</ErrorTextContainer>
	);
}
