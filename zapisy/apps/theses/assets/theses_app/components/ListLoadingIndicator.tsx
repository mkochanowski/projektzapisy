import * as React from "react";
import spinner from "./spinner_transparent.gif";

export function ListLoadingIndicator(): JSX.Element {
	return <div
		style={{
			textAlign: "center",
			width: "100%",
			marginTop: "-40px",
		}}
	>
		<img
			src={spinner}
			alt="Pobieranie listy prac..."
			style={{ width: "200px" }}
		/>;
	</div>;
}
