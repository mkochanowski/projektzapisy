import * as React from "react";
import styled from "styled-components";

import { Thesis } from "../../../types";
import { DateUpdatedPicker } from "./DateUpdatedPicker";
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
};

function ReservationCheckbox(props: {
	value: boolean, onChange: (val: boolean) => void
}) {
	return <label style={{ userSelect: "none" }}>
		<input
			type="checkbox"
			checked={props.value}
			style={{ position: "relative", verticalAlign: "middle" }}
		/> {"rezerwacja"}
	</label>;
}

export class ThesisTopRow extends React.Component<Props> {
	public render() {
		return <TopRowContainer>
			<ReservationCheckbox
				onChange={() => ({})}
				value={this.props.thesis.reserved}
			/>
			<DateUpdatedPicker
				onChange={() => ({})}
				value={this.props.thesis.modifiedDate}
			/>
			<ThesisStatusIndicator
				onChange={() => console.warn("status changed")}
				value={this.props.thesis.status}
			/>
		</TopRowContainer>;
	}
}
