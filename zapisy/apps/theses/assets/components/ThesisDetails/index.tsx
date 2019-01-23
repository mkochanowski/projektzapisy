import * as React from "react";
import Button from "react-button-component";
import styled from "styled-components";
import update from "immutability-helper";
import * as Mousetrap from "mousetrap";
import "mousetrap-global-bind";
import { Moment } from "moment";

import { ThesisTopRow } from "./ThesisTopRow";
import { ThesisMiddleForm } from "./ThesisMiddleForm";
import { ThesisVotes } from "./ThesisVotes";
import "./style.less";
import { Spinner } from "../Spinner";
import { getDisabledStyle } from "../../utils";
import { ThesisWorkMode, ApplicationState } from "../../app_types";
import { canModifyThesis } from "../../permissions";
import { Thesis } from "../../thesis";
import { Employee, Student } from "../../users";
import { ThesisStatus, ThesisKind } from "../../protocol_types";
import { AppMode } from "../../app_logic/app_mode";

const SaveButton = React.memo(Button.extend`
	&:disabled:hover {
		background: white;
	}
	&:disabled {
		color: grey;
		cursor: default;
	}
	min-height: initial;
	height: 25px;
`);

const DetailsSectionWrapper = styled.div`
	display: flex;
	justify-content: center;
	align-items: center;
`;

const MainDetailsContainer = styled.div`
	border: 1px solid black;
	padding: 15px;
	display: flex;
	flex-direction: row;
	width: 100%;
`;

const LeftDetailsContainer = styled.div`
	width: 790px;
`;

const RightDetailsContainer = styled.div`
	width: 100px;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
	margin-left: 20px;
`;

type Props = {
	thesis: Thesis;
	appState: ApplicationState;
	hasUnsavedChanges: boolean;
	mode: ThesisWorkMode;
	hasTitleError: boolean;
	onThesisModified: (thesis: Thesis) => void;
	onSaveRequested: () => void;
	onChangedTitle: () => void;
};

export class ThesisDetails extends React.PureComponent<Props> {
	public componentDidMount() {
		Mousetrap.bindGlobal("ctrl+s", ev => {
			if (this.props.hasUnsavedChanges) {
				this.props.onSaveRequested();
			}
			ev.preventDefault();
		});
	}

	public componentWillUnmount() {
		Mousetrap.unbindGlobal("ctrl+s");
	}

	public render() {
		return <DetailsSectionWrapper>
			{this.props.appState === ApplicationState.Saving
				? <Spinner style={{ position: "absolute" }}/>
				: null
			}
			<MainDetailsContainer
				style={AppMode.isPerformingBackendOp() ? getDisabledStyle() : {}}
			>
				<LeftDetailsContainer>{this.renderThesisLeftPanel()}</LeftDetailsContainer>
				<RightDetailsContainer>{this.renderThesisRightPanel()}</RightDetailsContainer>
			</MainDetailsContainer>
		</DetailsSectionWrapper>;
	}

	private renderThesisLeftPanel() {
		const { thesis } = this.props;
		return <>
			<ThesisTopRow
				mode={this.props.mode}
				thesis={thesis}
				onReservedUntilChanged={this.onReservedUntilChanged}
				onStatusChanged={this.onStatusChanged}
			/>
			<ThesisMiddleForm
				thesis={thesis}
				titleError={this.props.hasTitleError}
				onTitleChanged={this.onTitleChanged}
				onKindChanged={this.onKindChanged}
				onAdvisorChanged={this.onAdvisorChanged}
				onAuxAdvisorChanged={this.onAuxAdvisorChanged}
				onStudentChanged={this.onStudentChanged}
				onSecondStudentChanged={this.onSecondStudentChanged}
				onDescriptionChanged={this.onDescriptionChanged}
			/>
		</>;
	}

	private renderThesisRightPanel() {
		return <>
			<ThesisVotes/>
			{this.renderSaveButton()}
		</>;
	}

	private renderSaveButton() {
		const readOnly = !canModifyThesis(this.props.thesis);
		if (readOnly) {
			return null;
		}
		const { hasUnsavedChanges } = this.props;
		return <SaveButton
			onClick={this.props.onSaveRequested}
			disabled={!hasUnsavedChanges}
			title={hasUnsavedChanges ? this.getActionDescription() : "Nie dokonano zmian"}
		>{this.getActionTitle()}</SaveButton>;
	}

	private getActionTitle() {
		return this.props.mode === ThesisWorkMode.Adding ? "Dodaj" : "Zapisz";
	}

	private getActionDescription() {
		return this.props.mode === ThesisWorkMode.Adding ? "Dodaj nową pracę" : "Zapisz zmiany";
	}

	private updateThesisState(updateObject: object) {
		this.props.onThesisModified(
			update(this.props.thesis, updateObject)
		);
	}

	private onReservedUntilChanged = (newDate: Moment): void => {
		this.updateThesisState({ reservedUntil: { $set: newDate } });
	}

	private onStatusChanged = (newStatus: ThesisStatus): void => {
		this.updateThesisState({ status: { $set: newStatus } });
	}

	private onTitleChanged = (newTitle: string): void => {
		// As soon as the user changes the title, we clear the error state
		// it would be annoying if it stayed on until Save is clicked again
		this.props.onChangedTitle();
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

	private onStudentChanged = (newStudent: Student | null): void => {
		this.updateThesisState({ student: { $set: newStudent } });
	}

	private onSecondStudentChanged = (newSecondStudent: Student | null): void => {
		this.updateThesisState({ secondStudent: { $set: newSecondStudent } });
	}

	private onDescriptionChanged = (newDesc: string): void => {
		this.updateThesisState({ description: { $set: newDesc } });
	}
}
