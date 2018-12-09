import * as React from "react";

export function ReadOnlyInput(props: { text: string }) {
	return <input
		type={"text"}
		readOnly
		value={props.text}
		style={{ width: "100%", boxSizing: "border-box" }}
	/>;
}
