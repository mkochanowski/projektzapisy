import * as React from "react";
import spinner from "../spinner_transparent.gif";

export function SavingIndicator(): JSX.Element {
	return <img
			src={spinner}
			alt="Trwa zapisywanie danych..."
			style={{
				position: "absolute",
				zIndex: 999,
				width: "300px",
			}}
	/>;
}
