import * as React from "react";
import { CustomColumnComponentProps } from "griddle-react";

export function ReservationIndicator(props: CustomColumnComponentProps<any>): JSX.Element {
	return <input
		type={"checkbox"}
		checked={props.data}
		style={{ cursor: "default" }}
		disabled
		onClick={eatEvent}
	></input>;
}

function eatEvent(e: React.MouseEvent<HTMLInputElement>) {
	e.preventDefault();
	e.stopPropagation();
	return false;
}
