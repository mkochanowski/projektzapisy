import * as React from "react";
import styled from "styled-components";
import { Moment } from "moment";

import { Thesis, ThesisStatus } from "../../../types";
import { DateUpdatedField } from "./DateUpdatedField";
import { ThesisStatusIndicator } from "./ThesisStatusIndicator";

const TopRowContainer = styled.div`
display: flex;
flex-direction: row;
grid-column-gap: 10px;
column-gap: 10px;
justify-content: space-between;
width: 100%;
`;

type Props = {
	thesis: Thesis;
	onReservationChanged: (nr: boolean) => void;
	onDateChanged: (nd: Moment) => void;
	onStatusChanged: (ns: ThesisStatus) => void;
};

function ReservationCheckbox(props: {
	value: boolean, onChange: (val: boolean) => void
}) {
	return <label style={{ userSelect: "none" }}>
		<input
			type="checkbox"
			checked={props.value}
			onChange={ev => props.onChange(ev.target.checked)}
			style={{ position: "relative", verticalAlign: "middle" }}
		/> {"rezerwacja"}
	</label>;
}

export class ThesisTopRow extends React.Component<Props> {
	public render() {
		return <TopRowContainer>
			<ReservationCheckbox
				onChange={this.props.onReservationChanged}
				value={this.props.thesis.reserved}
			/>
			<DateUpdatedField
				value={this.props.thesis.modifiedDate}
			/>
			<ThesisStatusIndicator
				onChange={this.props.onStatusChanged}
				value={this.props.thesis.status}
			/>
		</TopRowContainer>;
	}
}
