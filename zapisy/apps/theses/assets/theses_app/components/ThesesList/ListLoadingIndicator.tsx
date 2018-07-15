import * as React from "react";
import spinner from "./spinner.gif";

export function ListLoadingIndicator(): JSX.Element {
	return <div
		style={{
			textAlign: "center",
			width: "100%",
		}}
	>
		<img src={spinner} alt="Loading..." />
	</div>;
}
