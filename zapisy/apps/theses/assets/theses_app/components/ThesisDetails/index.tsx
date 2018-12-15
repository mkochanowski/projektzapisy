import * as React from "react";
import Button from "react-button-component";
import styled from "styled-components";
import update from "immutability-helper";
import { Moment } from "moment";

import { Thesis, ThesisStatus, ThesisKind, Employee, AppUser, ThesisVote } from "../../types";
import { ThesisTopRow } from "./ThesisTopRow";
import { ThesisMiddleForm } from "./ThesisMiddleForm";
import { ThesisVotes } from "./ThesisVotes";

import { Spinner } from "../Spinner";
import { getDisabledStyle } from "../../utils";
import { ThesisWorkMode } from "../../types/misc";
import { canModifyThesis } from "../../permissions";

const SaveButton = Button.extend`
	&:disabled:hover {
		background: white;
	}
	&:disabled {
		color: grey;
		cursor: default;
	}
	height: 25px;
	min-height: 25px;
	max-height: 25px;
`;

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
flex-basis: 85%;
`;

const RightDetailsContainer = styled.div`
display: flex;
flex-direction: column;
justify-content: space-between;
margin-left: 20px;
`;

type Props = {
	thesis: Thesis;
	thesesList: Thesis[];
	thesesBoard: Employee[],
	isSaving: boolean;
	hasUnsavedChanges: boolean;
	mode: ThesisWorkMode;
	user: AppUser;
	onThesisModified: (thesis: Thesis) => void;
	onSaveRequested: () => void;
};

const initialState = {
	hasTitleError: false,
};
type State = typeof initialState;

export class ThesisDetails extends React.PureComponent<Props, State> {
	state = initialState;

	public render() {
		console.warn("Render details");

		return <DetailsSectionWrapper>
			{this.props.isSaving ? <Spinner style={{ position: "absolute" }}/> : null}
			<MainDetailsContainer
				style={this.props.isSaving ? getDisabledStyle() : {}}
			>
				<LeftDetailsContainer>{this.renderThesisLeftPanel()}</LeftDetailsContainer>
				<RightDetailsContainer>{this.renderThesisRightPanel()}</RightDetailsContainer>
			</MainDetailsContainer>
		</DetailsSectionWrapper>;
	}

	private renderThesisLeftPanel() {
		return <>
			<ThesisTopRow
				thesis={this.props.thesis}
				mode={this.props.mode}
				user={this.props.user}
				onReservationChanged={this.onReservationChanged}
				onDateChanged={this.onDateUpdatedChanged}
				onStatusChanged={this.onStatusChanged}
			/>
			<ThesisMiddleForm
				thesis={this.props.thesis}
				titleError={this.state.hasTitleError}
				user={this.props.user}
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
			<ThesisVotes
				thesis={this.props.thesis}
				thesesBoard={this.props.thesesBoard}
				onChange={this.onVoteChanged}
			/>
			{this.renderSaveButton()}
		</>;
	}

	private renderSaveButton() {
		const readOnly = !canModifyThesis(this.props.user, this.props.thesis);
		if (readOnly) {
			return null;
		}
		const { hasUnsavedChanges } = this.props;
		return <SaveButton
			onClick={this.handleSave}
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
		this.setState({ hasTitleError: false });
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

	private onVoteChanged = (voter: Employee, newValue: ThesisVote): void => {
		const newVotes = Object.assign({}, this.props.thesis.votes, {
			[voter.id]: newValue,
		});
		this.updateThesisState({ votes: { $set: newVotes } });
	}

	private validateBeforeSave() {
		const { thesis, thesesList } = this.props;
		const trimmedTitle = thesis.title.trim();
		if (!trimmedTitle) {
			window.alert("Tytuł pracy nie może być pusty.");
			this.setState({ hasTitleError: true });
			return false;
		}
		if (thesesList.find(t => !t.isEqual(thesis) && t.title.trim() === trimmedTitle)) {
			window.alert("Istnieje już inna praca o tym tytule.");
			this.setState({ hasTitleError: true });
			return false;
		}

		this.setState({ hasTitleError: false });
		return true;
	}

	private handleSave = () => {
		if (!this.validateBeforeSave()) {
			return;
		}

		this.props.onSaveRequested();
	}
}
