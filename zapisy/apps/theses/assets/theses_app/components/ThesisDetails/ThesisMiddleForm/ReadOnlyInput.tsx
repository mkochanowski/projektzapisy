import * as React from "react";

type Props = {
	text: string;
	style?: React.CSSProperties;
};

export function ReadOnlyInput(props: Props) {
	return <input
		type={"text"}
		readOnly
		value={props.text}
		style={props.style || {}}
	/>;
}
