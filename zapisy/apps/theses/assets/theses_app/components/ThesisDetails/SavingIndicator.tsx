import * as React from "react";
import spinner from "../spinner.gif";

export function SavingIndicator(): JSX.Element {
	return <div
		style={{
			textAlign: "center",
			width: "100%",
		}}
	>
		<img src={spinner} alt="Trwa zapisywanie danych..." />
	</div>;
}
