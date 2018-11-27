import * as React from "react";
import { Spinner } from "../Spinner";

export function LoadingIndicator() {
	return <div
		style={{
			width: "100%",
			textAlign: "center",
		}}
	>
		<Spinner/>;
	</div>;
}
