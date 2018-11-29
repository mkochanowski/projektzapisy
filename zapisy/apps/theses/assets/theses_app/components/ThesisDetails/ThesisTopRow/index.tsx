import * as React from "react";
import styled from "styled-components";
import { Moment } from "moment";

import { Thesis, ThesisStatus } from "../../../types";
import { ThesisDateField } from "./ThesisDateField";
import { ThesisStatusIndicator } from "./ThesisStatusIndicator";
import { ThesisWorkMode } from "../../../types/misc";

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
	mode: ThesisWorkMode;
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
		const { mode, thesis } = this.props;
		return <TopRowContainer>
			<ReservationCheckbox
				onChange={this.props.onReservationChanged}
				value={thesis.reserved}
			/>
			<ThesisDateField
				value={mode === ThesisWorkMode.Editing ? thesis.modifiedDate : undefined}
				label={"Aktualizacja"}
			/>
			<ThesisStatusIndicator
				onChange={this.props.onStatusChanged}
				value={thesis.status}
			/>
		</TopRowContainer>;
	}
}
