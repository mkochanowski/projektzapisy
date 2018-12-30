/**
 * @file The main theses app component.
 * Renders all subcomponents and glues them together, also permitting them
 * to change the state via callbacks.
 * Application state is generally held in theses_store.
 */

import * as React from "react";
import * as Mousetrap from "mousetrap";
import "mousetrap-global-bind";
import { observer } from "mobx-react";
import styled from "styled-components";
import { confirmAlert } from "react-confirm-alert";
import "react-confirm-alert/src/react-confirm-alert.css";

import { Thesis, ThesisTypeFilter } from "../types";
import { ThesisDetails } from "./ThesisDetails";
import { ThesesTable } from "./ThesesTable";
import { ErrorBox } from "./ErrorBox";
import { canAddThesis, canSetArbitraryAdvisor } from "../permissions";
import { ListFilters } from "./ListFilters";
import { AddNewButton } from "./AddNewButton";
import { thesesStore as store, LoadMode } from "../theses_store";
import { ThesisWorkMode, SortColumn, SortDirection } from "../types/misc";
import { ThesisNameConflict, ThesisEmptyTitle } from "../errors";
import { withAlert } from "react-alert";

const TopRowContainer = styled.div`
	display: flex;
	justify-content: space-between;
`;

const initialState = {
	/** The error instance, if any. If one exists, we abort the app and display it */
	applicationError: null as Error | null,
	/** Whether the thesis title was invalid */
	hasTitleError: false,
};
type State = typeof initialState;

@observer
class ThesesAppInternal extends React.Component<any, State> {
	state = initialState;
	private oldOnBeforeUnload: ((this: WindowEventHandlers, ev: BeforeUnloadEvent) => any) | null = null;
	private tableInstance: ThesesTable;

	componentDidMount() {
		store.initialize();

		this.oldOnBeforeUnload = window.onbeforeunload;
		window.onbeforeunload = this.confirmUnload;
		this.initializeKeyboardShortcuts();
		store.registerOnListChanged(this.onListChanged);
		store.registerOnError(this.onError);
	}

	private onListChanged = (mode: LoadMode) => {
		this.tableInstance.onListDidChange(mode);
	}

	private onError = (err: Error) => {
		this.setState({ applicationError: err });
	}

	componentWillUnmount() {
		window.onbeforeunload = this.oldOnBeforeUnload;
		this.deconfigureKeyboardShortcuts();
		store.clearOnListChanged();
		store.clearOnError();
	}

	private initializeKeyboardShortcuts() {
		Mousetrap.bindGlobal("ctrl+m", this.setupForAddingThesis);
		Mousetrap.bindGlobal("esc", this.onResetChanges);
	}

	private deconfigureKeyboardShortcuts() {
		Mousetrap.unbindGlobal(["ctrl+m", "esc"]);
	}

	private confirmUnload = (ev: BeforeUnloadEvent) => {
		if (store.hasUnsavedChanges()) {
			// As specified in https://developer.mozilla.org/en-US/docs/Web/API/WindowEventHandlers/onbeforeunload
			// preventDefault() is what the spec says,
			// in practice some browsers like returnValue to be set
			ev.preventDefault();
			ev.returnValue = "";
		}
	}

	private onTypeFilterChanged = (t: ThesisTypeFilter) => store.onTypeFilterChanged(t);
	private onAdvisorChanged = (a: string) => store.onAdvisorFilterChanged(a);
	private onTitleChanged = (t: string) => store.onTitleFilterChanged(t);
	private renderTopRow() {
		const shouldShowNewBtn = canAddThesis(store.user);
		return <TopRowContainer>
			<ListFilters
				onTypeChange={this.onTypeFilterChanged}
				typeValue={store.params.type}
				onAdvisorChange={this.onAdvisorChanged}
				advisorValue={store.params.advisor}
				onTitleChange={this.onTitleChanged}
				titleValue={store.params.title}
				state={store.applicationState}
				stringFilterBeingChanged={store.stringFilterBeingChanged}
			/>
			{shouldShowNewBtn ? <AddNewButton onClick={this.setupForAddingThesis}/> : null}
		</TopRowContainer>;
	}

	/** Stores the child table component so that we can tell it when the list changes */
	private setTableInstance = (table: ThesesTable) => {
		this.tableInstance = table;
	}

	private onLoadMore = async (_: number, until: number) => { await store.loadMore(until); };
	private onSortChanged = (col: SortColumn, dir: SortDirection) => store.onSortChanged(col, dir);
	private renderThesesList() {
		return <ThesesTable
			ref={this.setTableInstance}
			applicationState={store.applicationState}
			theses={store.theses}
			selectedIdx={store.selectedIdx}
			sortColumn={store.params.sortColumn}
			sortDirection={store.params.sortDirection}
			isEditingThesis={store.hasUnsavedChanges()}
			totalThesesCount={store.totalCount}
			onThesisSelected={this.onThesisSelected}
			onSortChanged={this.onSortChanged}
			loadMoreRows={this.onLoadMore}
		/>;
	}

	private onThesisModified = (nt: Thesis) => { store.updateModifiedThesis(nt); };
	private onChangedTitle = () => {
		if (this.state.hasTitleError) {
			this.setState({ hasTitleError: false });
		}
	}
	private renderThesisDetails() {
		return <ThesisDetails
			thesis={store.thesis!.modified}
			appState={store.applicationState}
			hasUnsavedChanges={store.hasUnsavedChanges()}
			mode={store.workMode!}
			user={store.user}
			hasTitleError={this.state.hasTitleError}
			onChangedTitle={this.onChangedTitle}
			onSaveRequested={this.onSave}
			onThesisModified={this.onThesisModified}
		/>;
	}

	public render() {
		if (this.state.applicationError) {
			return this.renderErrorScreen();
		}
		const { thesis } = store;
		if (thesis !== null) {
			// if a thesis is present, we're not just viewing
			console.assert(store.workMode !== ThesisWorkMode.Viewing);
		}
		return <>
			{this.renderTopRow()}
			<br />
			{this.renderThesesList()}
			{
				thesis
				? <><br /><hr />{this.renderThesisDetails()}</>
				: null
			}
		</>;
	}

	private renderErrorScreen() {
		return <ErrorBox
			errorTitle={
				<em>{this.state.applicationError!.toString()}</em>
			}
		/>;
	}

	/**
	 * If there are unsaved changes, ask the user whether they should be discarded.
	 * Returns true immediately if there are no changes to be saved.
	 */
	private confirmDiscardChanges() {
		if (store.hasUnsavedChanges()) {
			return new Promise((resolve) => {
				const title = store.thesis!.modified.title;
				const msg = buildUnsavedConfirmation(title);
				confirmAlert({
					title: "",
					message: msg,
					buttons: [
						{
							label: "Tak, porzuć",
							onClick: () => resolve(true),
						},
						{
							label: "Nie, wróć",
							onClick: () => resolve(false),
						}
					],
				});
			});
		}
		return Promise.resolve(true);
	}

	private onThesisSelected = async (thesis: Thesis) => {
		if (!await this.confirmDiscardChanges()) {
			return;
		}
		this.setState({ hasTitleError: false });
		store.selectThesis(thesis);
	}

	private setupForAddingThesis = async () => {
		if (!canAddThesis(store.user) || !await this.confirmDiscardChanges()) {
			return;
		}
		const thesis = new Thesis();
		if (!canSetArbitraryAdvisor(store.user)) {
			thesis.advisor = store.user.user;
		}
		this.setState({ hasTitleError: false });
		store.setupForNewThesis(thesis);
	}

	private onResetChanges = async () => {
		if (!await this.confirmDiscardChanges()) {
			return;
		}
		store.resetModifiedThesis();
	}

	private onSave = async () => {
		try {
			const oldWorkMode = store.workMode;
			await store.save();
			this.props.alert.success(messageForWorkMode(oldWorkMode));
		} catch (err) {
			this.handleSaveError(err);
		}
	}

	private handleSaveError(err: Error) {
		if (err instanceof ThesisNameConflict) {
			this.props.alert.error("Praca o tym tytule już istnieje.");
			this.setState({ hasTitleError: true });
		} else if (err instanceof ThesisEmptyTitle) {
			this.props.alert.error("Tytuł pracy nie może być pusty");
			this.setState({ hasTitleError: true });
		} else {
			const msg = (
				`Nie udało się zapisać pracy (${err}). ` +
				"Odśwież stronę/sprawdź połączenie sieciowe i spróbuj jeszcze raz. " +
				"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów."
			);
			// This isn't a confirmation message, but that component can also
			// be used for modal alerts
			confirmAlert({
				title: "Błąd",
				message: msg,
				buttons: [{ label: "OK" }],
			});
		}
	}
}

function buildUnsavedConfirmation(title: string) {
	return title.trim()
		? `Czy porzucić niezapisane zmiany w pracy "${title}"?`
		: "Czy porzucić niezapisane zmiany w edytowanej pracy?";
}

function messageForWorkMode(mode: ThesisWorkMode) {
	switch (mode) {
		case ThesisWorkMode.Adding: return "Praca została dodana";
		case ThesisWorkMode.Editing: return "Zapisano zmiany";
		default: throw new Error("bad work mode");
	}
}

export const ThesesApp = withAlert(ThesesAppInternal);
