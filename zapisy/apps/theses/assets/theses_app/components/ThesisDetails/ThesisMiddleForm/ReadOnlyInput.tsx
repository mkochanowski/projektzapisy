import * as React from "react";

type Props = {
	text: string;
	style?: React.CSSProperties;
};

export function ReadOnlyInput(props: Props) {
	const baseStyle = { width: "100%", boxSizing: "border-box" };
	const finalStyle = Object.assign({}, props.style, baseStyle);
	return <input
		type={"text"}
		readOnly
		value={props.text}
		style={finalStyle}
	/>;
}
