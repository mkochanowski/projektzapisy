import * as React from "react";

type Props = {
	reserved: boolean;
};

export function ReservationIndicator(props: Props): JSX.Element {
	return <input
		type={"checkbox"}
		checked={props.reserved}
		readOnly
		style={{ cursor: "default" }}
	></input>;
}
