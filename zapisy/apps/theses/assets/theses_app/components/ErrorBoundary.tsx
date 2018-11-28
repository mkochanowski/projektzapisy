import * as React from "react";
import styled from "styled-components";

const ErrorTextContainer = styled.div`
width: 100%;
padding: 40px;
text-align: center;
`;

type Props = {};
type State = {
	error: Error | null;
};

export class ErrorBoundary extends React.Component<Props, State> {
	public constructor(props: Props) {
		super(props);
		this.state = {
			error: null,
		};
	}

	public componentDidCatch(error: Error): void {
		this.setState({ error });
	}

	public render() {
		if (this.state.error) {
			return <ErrorTextContainer>
				<h2>Coś poszło nie tak</h2>
				<h3>Wystąpił błąd: <em>{this.state.error.toString()}</em></h3>
				<br />
				<p>Spróbuj załadować stronę od nowa. Jeżeli problem powtórzy się, opisz go na trackerze Zapisów.</p>
			</ErrorTextContainer>;
		}
		return this.props.children;
	}
}
