import * as React from "react";
import Button from "react-button-component";
import styled from "styled-components";
import update from "immutability-helper";
import * as Mousetrap from "mousetrap";
import "mousetrap-global-bind";
import * as moment from "moment";

import { ThesisTopRow } from "./ThesisTopRow";
import { ThesisMiddleForm } from "./ThesisMiddleForm";
import { ThesisVotes } from "./ThesisVotes";
import "./style.less";
import { Spinner } from "../Spinner";
import { getDisabledStyle, macosifyKeys } from "../../utils";
import { ThesisWorkMode, ApplicationState } from "../../app_types";
import { canModifyThesis, canDeleteThesis } from "../../permissions";
import { Thesis } from "../../thesis";
import { Employee, Student } from "../../users";
import { ThesisStatus, ThesisKind } from "../../protocol_types";
import { AppMode } from "../../app_logic/app_mode";
import { confirmationDialog } from "../Dialogs/ConfirmationDialog";
import { formatTitle } from "../util";

const ActionButton = React.memo(Button.extend`
	&:disabled:hover {
		background: white;
	}
	&:disabled {
		color: grey;
		cursor: default;
	}../Dialogs/Dialogs
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

const ButtonsContainer = styled.div`
	display: grid;
	grid-gap: 10px;
`;

const DEFAULT_THESIS_RESERVATION_YEARS = 2;

type Props = {
	thesis: Thesis;
	original: Thesis;
	appState: ApplicationState;
	hasUnsavedChanges: boolean;
	mode: ThesisWorkMode;
	hasTitleError: boolean;
	onThesisModified: (thesis: Thesis) => void;
	onDeletionRequested: () => Promise<void>;
	onSaveRequested: () => Promise<void>;
	onResetRequested: () => void;
	onChangedTitle: () => void;
};

export class ThesisDetails extends React.PureComponent<Props> {
	private actionInProgress: boolean = false;

	public componentDidMount() {
		Mousetrap.bindGlobal(macosifyKeys("ctrl+s"), ev => {
			this.handleSave();
			ev.preventDefault();
		});
		Mousetrap.bind("del", () => {
			this.handleDelete();
		});
	}

	public componentWillUnmount() {
		Mousetrap.unbindGlobal(macosifyKeys("ctrl+s"));
		Mousetrap.unbind("del");
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
		const { thesis, original } = this.props;
		return <>
			<ThesisTopRow
				mode={this.props.mode}
				thesis={thesis}
				original={original}
				onReservedUntilChanged={this.onReservedUntilChanged}
				onStatusChanged={this.onStatusChanged}
			/>
			<ThesisMiddleForm
				thesis={thesis}
				original={original}
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
			<ButtonsContainer>
				{this.renderResetButton()}
				{this.renderDeleteButton()}
				{this.renderSaveButton()}
			</ButtonsContainer>
		</>;
	}

	private renderResetButton() {
		if (!canModifyThesis(this.props.original)) {
			return null;
		}
		const { hasUnsavedChanges } = this.props;
		return <ActionButton
			onClick={this.props.onResetRequested}
			disabled={!hasUnsavedChanges}
			title={hasUnsavedChanges ? "Wycofaj dokonane zmiany" : "Nie dokonano zmian"}
		>Wyczyść</ActionButton>;
	}

	private renderDeleteButton() {
		if (this.props.mode === ThesisWorkMode.Adding || !canDeleteThesis(this.props.original)) {
			return null;
		}
		return <ActionButton
			onClick={this.handleDelete}
			title={"Usuń pracę z systemu"}
		>Usuń</ActionButton>;
	}

	private renderSaveButton() {
		if (!canModifyThesis(this.props.original)) {
			return null;
		}
		const { hasUnsavedChanges } = this.props;
		return <ActionButton
			onClick={this.handleSave}
			disabled={!hasUnsavedChanges}
			title={hasUnsavedChanges ? this.getActionDescription() : "Nie dokonano zmian"}
		>{this.getActionTitle()}</ActionButton>;
	}

	private getActionTitle() {
		return this.props.mode === ThesisWorkMode.Adding ? "Dodaj" : "Zapisz";
	}

	private getActionDescription() {
		return this.props.mode === ThesisWorkMode.Adding ? "Dodaj nową pracę" : "Zapisz zmiany";
	}

	private handleDelete = async () => {
		if (this.actionInProgress || !canDeleteThesis(this.props.original)) {
			return;
		}
		this.actionInProgress = true;
		const confirmed = await confirmationDialog({
			message: <>Czy usunąć pracę {formatTitle(this.props.thesis.title)}?</>,
			yesText: "Tak, usuń",
			noText: "Nie, wróć",
		});
		if (confirmed) {
			await this.props.onDeletionRequested();
		}
		this.actionInProgress = false;
	}

	private async confirmArchiveThesis() {
		return confirmationDialog({
			message: <>Czy zarchiwizować pracę {formatTitle(this.props.thesis.title)}?
			Dalszej edycji dokonywać będzie mógł wyłącznie administrator systemu.</>,
			yesText: "Tak, zarchiwizuj",
			noText: "Nie, wróć",
		});
	}

	private handleSave = async () => {
		if (this.actionInProgress || !this.props.hasUnsavedChanges) { return; }
		this.actionInProgress = true;
		const { original, thesis } = this.props;
		if (
			original.status === ThesisStatus.Defended ||
			thesis.status !== ThesisStatus.Defended ||
			await this.confirmArchiveThesis()
		) {
			await this.props.onSaveRequested();
		}
		this.actionInProgress = false;
	}

	private updateThesisState(updateObject: object) {
		this.props.onThesisModified(
			update(this.props.thesis, updateObject)
		);
	}

	private onReservedUntilChanged = (newDate: moment.Moment): void => {
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
		// also update the reservation date, but only if they haven't touched it previously
		const { original, thesis } = this.props;
		const update = { student: { $set: newStudent } };
		if (original.isReservationDateSame(thesis.reservedUntil)) {
			const expires = moment().add(DEFAULT_THESIS_RESERVATION_YEARS, "years");
			Object.assign(update, { reservedUntil: { $set: expires } });
		}
		this.updateThesisState(update);
	}

	private onSecondStudentChanged = (newSecondStudent: Student | null): void => {
		this.updateThesisState({ secondStudent: { $set: newSecondStudent } });
	}

	private onDescriptionChanged = (newDesc: string): void => {
		this.updateThesisState({ description: { $set: newDesc } });
	}
}
