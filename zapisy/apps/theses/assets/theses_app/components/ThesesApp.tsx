/**
 * @file The main theses app component.
 * Renders all subcomponents and glues them together, also permitting them
 * to change the state via callbacks.
 */

import * as React from "react";
import * as Mousetrap from "mousetrap";
import { observer } from "mobx-react";
import styled from "styled-components";

import { Thesis } from "../types";
import { ThesisDetails } from "./ThesisDetails";
import { ApplicationState } from "../types/misc";
import { ThesesTable } from "./ThesesTable";
import { ErrorBox } from "./ErrorBox";
import { canAddThesis, canSetArbitraryAdvisor } from "../permissions";
import { ListFilters } from "./ListFilters";
import { AddNewButton } from "./AddNewButton";
import { inRange } from "common/utils";
import { thesesStore as store } from "./theses_store";

const TopRowContainer = styled.div`
	display: flex;
	justify-content: space-between;
`;

@observer
export class ThesesApp extends React.Component {
	private oldOnBeforeUnload: ((this: WindowEventHandlers, ev: BeforeUnloadEvent) => any) | null = null;

	componentDidMount() {
		store.initialize();

		this.oldOnBeforeUnload = window.onbeforeunload;
		window.onbeforeunload = this.confirmUnload;
		this.initializeKeyboardShortcuts();
	}

	componentWillUnmount() {
		window.onbeforeunload = this.oldOnBeforeUnload;
		this.deconfigureKeyboardShortcuts();
	}

	private initializeKeyboardShortcuts() {
		Mousetrap.bind("ctrl+m", this.setupForAddingThesis);
		Mousetrap.bind("esc", this.onResetChanges);
	}

	private deconfigureKeyboardShortcuts() {
		Mousetrap.unbind(["ctrl+m", "esc"]);
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

	private renderTopRow() {
		const shouldShowNewBtn = canAddThesis(store.user);
		return <TopRowContainer>
			<ListFilters
				onTypeChange={store.onTypeFilterChanged}
				typeValue={store.params.type}
				onAdvisorChange={store.onAdvisorFilterChanged}
				advisorValue={store.params.advisor}
				onTitleChange={store.onTitleFilterChanged}
				titleValue={store.params.title}
				enabled={store.applicationState === ApplicationState.Normal}
			/>
			{shouldShowNewBtn ? <AddNewButton onClick={this.setupForAddingThesis}/> : null}
		</TopRowContainer>;
	}

	private renderThesesList() {
		return <ThesesTable
			applicationState={store.applicationState}
			theses={store.theses}
			selectedIdx={store.selectedIdx}
			sortColumn={store.params.sortColumn}
			sortDirection={store.params.sortDirection}
			isEditingThesis={store.hasUnsavedChanges()}
			totalThesesCount={store.totalCount}
			onThesisSelected={this.onThesisSelected}
			switchToThesisWithOffset={this.switchWithOffset}
			onSortChanged={store.onSortChanged}
			loadMoreRows={async until => { await store.loadMore(until); }}
		/>;
	}

	private renderThesesDetails() {
		return <ThesisDetails
			thesis={store.thesis!.modified}
			appState={store.applicationState}
			hasUnsavedChanges={store.hasUnsavedChanges()}
			mode={store.workMode!}
			user={store.user}
			onSaveRequested={this.onSave}
			onThesisModified={store.updateModifiedThesis}
		/>;
	}

	public render() {
		if (store.fetchError) {
			return this.renderErrorScreen();
		}
		const { thesis } = store;
		const mainComponent = <>
			{this.renderTopRow()}
			<br />
			{this.renderThesesList()}
		</>;
		if (thesis !== null) {
			console.assert(store.workMode !== null);
			return <>
				{mainComponent}
				<br />
				<hr />
				{this.renderThesesDetails()}
			</>;
		 }
		 return mainComponent;
	}

	private renderErrorScreen() {
		return <ErrorBox
			errorTitle={
				<span>
					Nie udało się pobrać listy prac: <em>{store.fetchError!.toString()}</em>
				</span>
			}
		/>;
	}

	private confirmDiscardChanges() {
		if (store.hasUnsavedChanges()) {
			const title = store.thesis!.modified.title;
			return window.confirm(
				title
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
			window.alert(
				"Nie udało się zapisać pracy. Odśwież stronę i spróbuj jeszcze raz. " +
				"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów."
			);
		}
	}
}
