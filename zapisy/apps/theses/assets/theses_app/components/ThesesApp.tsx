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

import { Thesis, ThesisTypeFilter } from "../types";
import { ThesisDetails } from "./ThesisDetails";
import { ThesesTable } from "./ThesesTable";
import { ErrorBox } from "./ErrorBox";
import { canAddThesis, canSetArbitraryAdvisor } from "../permissions";
import { ListFilters } from "./ListFilters";
import { AddNewButton } from "./AddNewButton";
import { inRange } from "common/utils";
import { thesesStore as store, LoadMode } from "../theses_store";
import { ThesisWorkMode, SortColumn, SortDirection } from "../types/misc";
import { ThesisNameConflict } from "../errors";

const TopRowContainer = styled.div`
	display: flex;
	justify-content: space-between;
`;

const initialState = {
	/** The error instance, if any. If one exists, we abort the app and display it */
	applicationError: null as Error | null,
	/** Whether the last save attempt failed because of a duplicate title */
	hadDuplicateTitle: false,
};
type State = typeof initialState;

@observer
export class ThesesApp extends React.Component<any, State> {
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
				displayUngraded={store.isThesesBoardMember(store.user.user)}
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
			switchToThesisWithOffset={this.switchWithOffset}
			onSortChanged={this.onSortChanged}
			loadMoreRows={this.onLoadMore}
		/>;
	}

	private onThesisModified = (nt: Thesis) => store.updateModifiedThesis(nt);
	private renderThesisDetails() {
		return <ThesisDetails
			thesis={store.thesis!.modified}
			thesesBoard={store.thesesBoard}
			appState={store.applicationState}
			hasUnsavedChanges={store.hasUnsavedChanges()}
			mode={store.workMode!}
			user={store.user}
			hadDuplicateTitle={this.state.hadDuplicateTitle}
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
			const title = store.thesis!.modified.title;
			return window.confirm(
				title.trim()
					? `Czy porzucić niezapisane zmiany w pracy "${title}"?`
					: "Czy porzucić niezapisane zmiany?"
			);
		}
		return true;
	}

	private onThesisSelected = (thesis: Thesis) => {
		if (!this.confirmDiscardChanges()) {
			return;
		}
		store.selectThesis(thesis);
	}

	/** Switch to the thesis at the specified offset from the current thesis */
	public switchWithOffset = (offset: number) => {
		const { selectedIdx, theses } = store;
		if (selectedIdx === -1) {
			return;
		}
		const target = selectedIdx + offset;
		if (!inRange(target, 0, theses.length - 1)) {
			return;
		}
		this.onThesisSelected(theses[target]);
	}

	private setupForAddingThesis = () => {
		if (!canAddThesis(store.user)) {
			return;
		}
		const thesis = new Thesis();
		if (!canSetArbitraryAdvisor(store.user)) {
			thesis.advisor = store.user.user;
		}
		store.setupForNewThesis(thesis);
	}

	private onResetChanges = () => {
		if (!this.confirmDiscardChanges()) {
			return;
		}
		store.resetModifiedThesis();
	}

	private onSave = async () => {
		try {
			await store.save();
		} catch (err) {
			if (err instanceof ThesisNameConflict) {
				window.alert("Praca o tym tytule już istnieje.");
				this.setState({ hadDuplicateTitle: true });
			} else {
				window.alert(
					"Nie udało się zapisać pracy. Odśwież stronę i spróbuj jeszcze raz. " +
					"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów.\n\n" +
					`Szczegóły błędu: ${err}`
				);
			}
		}
	}
}
