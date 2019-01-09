/**
 * @file The top row of the thesis details view
 */
import * as React from "react";
import styled from "styled-components";
import { Moment } from "moment";

import { ThesisDateField } from "./ThesisDateField";
import { ThesisStatusIndicator } from "./ThesisStatusIndicator";
import { ThesisWorkMode } from "../../../app_types";
import { canChangeStatus, canModifyThesis } from "../../../permissions";
import { Thesis } from "../../../thesis";
import { AppUser } from "../../../users";
import { ThesisStatus } from "../../../protocol_types";

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
	user: AppUser;
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
		const readOnly = !canModifyThesis(this.props.thesis);
		const { mode, thesis } = this.props;
		return <TopRowContainer>
			<ReservationCheckbox
				onChange={this.props.onReservationChanged}
				value={thesis.reserved}
				enabled={!readOnly}
			/>
			<ThesisDateField
				value={mode === ThesisWorkMode.Editing ? thesis.modifiedDate : undefined}
				label={"Aktualizacja"}
			/>
			<ThesisStatusIndicator
				onChange={this.props.onStatusChanged}
				value={thesis.status}
				enabled={!readOnly && canChangeStatus()}
			/>
		</TopRowContainer>;
	}
}
