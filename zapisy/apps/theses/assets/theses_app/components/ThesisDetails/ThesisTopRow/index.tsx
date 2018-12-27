/**
 * @file The top row of the thesis details view
 */
import * as React from "react";
import styled from "styled-components";
import { Moment } from "moment";

import { ThesisStatus, AppUser } from "../../../types";
import { ThesisDateField } from "./ThesisDateField";
import { ThesisStatusIndicator } from "./ThesisStatusIndicator";
import { ThesisWorkMode } from "../../../types/misc";
import { canChangeStatus } from "../../../permissions";

const TopRowContainer = styled.div`
display: flex;
flex-direction: row;
grid-column-gap: 10px;
column-gap: 10px;
justify-content: space-between;
width: 100%;
`;

type Props = {
	mode: ThesisWorkMode;
	user: AppUser;
	readOnly: boolean;
	isReserved: boolean;
	dateChanged: Moment;
	status: ThesisStatus;
	onReservationChanged: (nr: boolean) => void;
	onDateChanged: (nd: Moment) => void;
	onStatusChanged: (ns: ThesisStatus) => void;
};

function ReservationCheckbox(props: {
	value: boolean,
	enabled: boolean,
	onChange: (val: boolean) => void
}) {
	return <label style={{ userSelect: "none" }}>
		<input
			type="checkbox"
			checked={props.value}
			disabled={!props.enabled}
			onChange={ev => props.onChange(ev.target.checked)}
			style={{
				position: "relative",
				verticalAlign: "middle",
				cursor: props.enabled ? "pointer" : "default",
			}}
		/> {"rezerwacja"}
	</label>;
}

export class ThesisTopRow extends React.PureComponent<Props> {
	public render() {
		const { mode, readOnly } = this.props;
		return <TopRowContainer>
			<ReservationCheckbox
				onChange={this.props.onReservationChanged}
				value={this.props.isReserved}
				enabled={!readOnly}
			/>
			<ThesisDateField
				value={mode === ThesisWorkMode.Editing ? this.props.dateChanged : undefined}
				label={"Aktualizacja"}
			/>
			<ThesisStatusIndicator
				onChange={this.props.onStatusChanged}
				value={this.props.status}
				enabled={!readOnly && canChangeStatus(this.props.user)}
			/>
		</TopRowContainer>;
	}
}
