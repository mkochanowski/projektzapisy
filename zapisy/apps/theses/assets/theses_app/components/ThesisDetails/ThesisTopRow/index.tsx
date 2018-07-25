import * as React from "react";

import { Thesis, ThesisStatus } from "../../../types";
import { DateUpdatedPicker } from "./DateUpdatedPicker";
import { ThesisStatusIndicator } from "./ThesisStatusIndicator";

type Props = {
	thesis: Thesis;
};

function ReservationCheckbox(props: {
	initialValue: boolean, onChange: (val: boolean) => void
}) {
	return <label style={{ userSelect: "none" }}>
		<input
			type="checkbox"
			defaultChecked={props.initialValue}
			style={{ position: "relative", verticalAlign: "middle" }}
		/> {"rezerwacja"}
	</label>;
}

export class ThesisTopRow extends React.Component<Props> {
	public render() {
		return <div style={{
			display: "flex",
			flexDirection: "row",
			gridColumnGap: "10px",
			columnGap: "10px",
			justifyContent: "space-between",
			width: "100%"
		}}>
			<ReservationCheckbox
				onChange={() => ({})}
				initialValue={this.props.thesis.reserved}
			/>
			<DateUpdatedPicker
				onChange={() => ({})}
				initialValue={this.props.thesis.modifiedDate}
			/>
			<ThesisStatusIndicator
				onChange={() => ({})}
				initialValue={this.props.thesis.status}
			/>
		</div>;
	}
}
