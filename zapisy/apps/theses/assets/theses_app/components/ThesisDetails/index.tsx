import * as React from "react";
import Button from "react-button-component";
import styled from "styled-components";
import { clone, isEqual } from "lodash";
import update, { Query } from "immutability-helper";

import { Thesis, ThesisStatus, ThesisKind, Employee } from "../../types";
import { ThesisTopRow } from "./ThesisTopRow";
import { ThesisMiddleForm } from "./ThesisMiddleForm";
import { ThesisVotes } from "./ThesisVotes";
import { Moment } from "moment";
import { saveModifiedThesis } from "../../backend_callers";

const SaveButton = Button.extend`
&:disabled:hover {
	background: white;
}
&:disabled {
	color: grey;
	cursor: default;
}
`;

const MainDetailsContainer = styled.div`
border: 1px solid black;
padding: 15px;
display: flex;
flex-direction: row;
`;

const LeftDetailsContainer = styled.div`
width: 100%;
`;

const RightDetailsContainer = styled.div`
display: flex;
flex-direction: column;
justify-content: space-between;
margin-left: 20px;
`;

type Props = {
	selectedThesis: Thesis,
};

type State = {
	currentThesis: Thesis;
};

export class ThesisDetails extends React.Component<Props, State> {
	public constructor(props: Props) {
		super(props);
		this.state = {
			currentThesis: clone(props.selectedThesis)
		};
	}

	public UNSAFE_componentWillReceiveProps(nextProps: Props) {
		console.error("Getting derived state");
		this.setState({
			currentThesis: clone(nextProps.selectedThesis)
		});
	}

	public render() {
		const shouldAllowSave = this.shouldAllowSave();
		return <MainDetailsContainer>
			<LeftDetailsContainer>
				<ThesisTopRow
					thesis={this.state.currentThesis}
					onReservationChanged={this.onReservationChanged}
					onDateChanged={this.onDateUpdatedChanged}
					onStatusChanged={this.onStatusChanged}
				/>
				<ThesisMiddleForm
					thesis={this.state.currentThesis}
					onTitleChanged={this.onTitleChanged}
					onKindChanged={this.onKindChanged}
					onAdvisorChanged={this.onAdvisorChanged}
					onAuxAdvisorChanged={this.onAuxAdvisorChanged}
					onStudentChanged={this.onStudentChanged}
					onSecondStudentChanged={this.onSecondStudentChanged}
					onDescriptionChanged={this.onDescriptionChanged}
				/>
			</LeftDetailsContainer>
			<RightDetailsContainer>
				<ThesisVotes />
				<SaveButton
					onClick={this.onSaveRequested}
					disabled={!shouldAllowSave}
					title={shouldAllowSave ? "Zapisz zmiany" : "Nie dokonano zmian"}
				>Zapisz</SaveButton>
			</RightDetailsContainer>
		</MainDetailsContainer>;
	}

	private shouldAllowSave(): boolean {
		console.warn(isEqual(this.state.currentThesis, this.props.selectedThesis));
		return !isEqual(this.state.currentThesis, this.props.selectedThesis);
	}

	private updateThesisState(updateObject: Query<Thesis>) {
		this.setState(update(this.state, { currentThesis: updateObject }));
	}

	private onReservationChanged = (newValue: boolean): void => {
		this.updateThesisState({ reserved: { $set: newValue } });
	}

	private onDateUpdatedChanged = (newDate: Moment): void => {
		this.updateThesisState({ modifiedDate: { $set: newDate } });
	}

	private onStatusChanged = (newStatus: ThesisStatus): void => {
		this.updateThesisState({ status: { $set: newStatus } });
	}

	private onTitleChanged = (newTitle: string): void => {
		this.updateThesisState({ title: { $set: newTitle } });
	}

	private onKindChanged = (newKind: ThesisKind): void => {
		this.updateThesisState({ kind: { $set: newKind } });
	}

	private onAdvisorChanged = (newAdvisor: Employee | null): void => {
		this.updateThesisState({ advisor: { $set: newAdvisor } });
	}

	private onAuxAdvisorChanged = (newAuxAdvisor: Employee | null): void => {
		this.updateThesisState({ auxiliaryAdvisor: { $set: newAuxAdvisor } });
	}

	private onStudentChanged = (newStudent: Employee | null): void => {
		this.updateThesisState({ student: { $set: newStudent } });
	}

	private onSecondStudentChanged = (newSecondStudent: Employee | null): void => {
		this.updateThesisState({ secondStudent: { $set: newSecondStudent } });
	}

	private onDescriptionChanged = (newDesc: string): void => {
		this.updateThesisState({ description: { $set: newDesc } });
	}

	private onSaveRequested = () => {
		console.warn("Save clicked");
		saveModifiedThesis(this.props.selectedThesis, this.state.currentThesis);
	}
}
