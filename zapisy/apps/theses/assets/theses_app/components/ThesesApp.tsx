/**
 * @file The main theses app component. It performs two basic tasks:
 * -> stores the global application-wide state
 * -> renders all subcomponents and glues them together, also permitting them
 * to change the state via callbacks
 */

import * as React from "react";
import * as Mousetrap from "mousetrap";
import { observer } from "mobx-react";
import { observable, action, flow, configure, computed } from "mobx";
import { clone } from "lodash";

import { Thesis, AppUser, ThesisTypeFilter } from "../types";
import {
	getThesesList, saveModifiedThesis, saveNewThesis,
	getCurrentUser, ThesesProcessParams, SortColumn, SortDirection, FAKE_USER,
} from "../backend_callers";
import { ThesisDetails } from "./ThesisDetails";
import { ApplicationState, ThesisWorkMode } from "../types/misc";
import { ThesesTable } from "./ThesesTable";
import { ErrorBox } from "./ErrorBox";
import { canAddThesis, canSetArbitraryAdvisor } from "../permissions";
import styled from "styled-components";
import { ListFilters } from "./ListFilters";
import { AddNewButton } from "./AddNewButton";
import { inRange } from "common/utils";
import { CancellablePromise } from "mobx/lib/api/flow";

const ROWS_PER_PAGE = 30;

configure({ enforceActions: "observed" });

/** The currently selected thesis */
type StateThesis = {
	/** Its original, unchanged version */
	original: Thesis;
	/** And the version the user is modifying */
	mutable: Thesis;
};

const TopRowContainer = styled.div`
	display: flex;
	justify-content: space-between;
`;

@observer
export class ThesesApp extends React.Component {
	@observable private theses: Thesis[] = [];
	@observable private thesis: StateThesis | null = null;
	@observable private currentPage: number = 1;
	@observable private user: AppUser = FAKE_USER;
	@observable private applicationState: ApplicationState = ApplicationState.InitialLoading;
	@observable private fetchError: Error | null = null;
	@observable private workMode: ThesisWorkMode = ThesisWorkMode.Viewing;
	@observable private totalCount: number = 0;
	@observable private params: ThesesProcessParams = observable({
		type: ThesisTypeFilter.Default,
		title: "",
		advisor: "",
		sortColumn: SortColumn.None,
		sortDirection: SortDirection.Asc,
	});

	private oldOnBeforeUnload: ((this: WindowEventHandlers, ev: BeforeUnloadEvent) => any) | null = null;

	@computed private get selectedIdx() {
		return thesisIndexInList(this.thesis && this.thesis.original, this.theses);
	}

	componentDidMount() {
		this.initializeState();

		this.oldOnBeforeUnload = window.onbeforeunload;
		window.onbeforeunload = this.confirmUnload;
		this.initializeKeyboardShortcuts();
	}

	private initializeState = flow(function* (this: ThesesApp) {
		this.user = yield getCurrentUser();
		yield this.refreshTheses();
		this.applicationState = ApplicationState.Normal;
	});

	componentWillUnmount() {
		window.onbeforeunload = this.oldOnBeforeUnload;
		this.deconfigureKeyboardShortcuts();
	}

	private initializeKeyboardShortcuts() {
		Mousetrap.bind("ctrl+m", this.setupForAddingThesis);
		Mousetrap.bind("esc", this.resetChanges);
	}

	private deconfigureKeyboardShortcuts() {
		Mousetrap.unbind(["ctrl+m", "esc"]);
	}

	private confirmUnload = (ev: BeforeUnloadEvent) => {
		if (this.hasUnsavedChanges()) {
			// As specified in https://developer.mozilla.org/en-US/docs/Web/API/WindowEventHandlers/onbeforeunload
			// preventDefault() is what the spec says,
			// in practice some browsers like returnValue to be set
			ev.preventDefault();
			ev.returnValue = "";
		}
	}

	private onFilterChanged() {
		this.currentPage = 1;
		this.refreshTheses();
	}
	@action
	private onTypeFilterChanged = (value: ThesisTypeFilter) => {
		this.params.type = value;
		this.onFilterChanged();
	}
	@action
	private onAdvisorFilterChanged = (value: string) => {
		this.params.advisor = value.toLowerCase();
		this.onFilterChanged();
	}
	@action
	private onTitleFilterChanged = (value: string) => {
		this.params.title = value.toLowerCase();
		this.onFilterChanged();
	}

	private renderTopRow() {
		const shouldShowNewBtn = canAddThesis(this.user);
		const { params } = this;
		return <TopRowContainer>
			<ListFilters
				onTypeChange={this.onTypeFilterChanged}
				typeValue={params.type}
				onAdvisorChange={this.onAdvisorFilterChanged}
				advisorValue={params.advisor}
				onTitleChange={this.onTitleFilterChanged}
				titleValue={params.title}
				enabled={this.applicationState === ApplicationState.Normal}
			/>
			{shouldShowNewBtn ? <AddNewButton onClick={this.setupForAddingThesis}/> : null}
		</TopRowContainer>;
	}

	@action
	private onSortChanged = (column: SortColumn, dir: SortDirection) => {
		this.params.sortColumn = column;
		this.params.sortDirection = dir;
		this.onFilterChanged();
	}

	private loadMoreForTable = (flow(function* (this: ThesesApp, _: number, stopIndex: number) {
		console.warn("render more", stopIndex);
		const page = indexToPage(stopIndex);
		if (page <= this.currentPage) {
			return;
		}
		this.currentPage = page;
		yield this.refreshTheses();
	}) as (_: number, stopIndex: number) => CancellablePromise<void>).bind(this);

	private renderThesesList() {
		return <ThesesTable
			applicationState={this.applicationState}
			theses={this.theses}
			selectedIdx={this.selectedIdx}
			sortColumn={this.params.sortColumn}
			sortDirection={this.params.sortDirection}
			isEditingThesis={this.hasUnsavedChanges()}
			totalThesesCount={this.totalCount}
			onThesisSelected={this.onThesisSelected}
			switchToThesisWithOffset={this.switchWithOffset}
			onSortChanged={this.onSortChanged}
			loadMoreRows={this.loadMoreForTable}
		/>;
	}

	private renderThesesDetails() {
		return <ThesisDetails
			thesis={this.thesis!.mutable}
			isSaving={this.applicationState === ApplicationState.PerformingBackendChanges}
			hasUnsavedChanges={this.hasUnsavedChanges()}
			mode={this.workMode!}
			user={this.user}
			onSaveRequested={this.handleThesisSave}
			onThesisModified={this.onThesisModified}
		/>;
	}

	public render() {
		if (this.fetchError) {
			return this.renderErrorScreen();
		}
		const { thesis } = this;
		const mainComponent = <>
			{this.renderTopRow()}
			<br />
			{this.renderThesesList()}
		</>;
		if (thesis !== null) {
			console.assert(this.workMode !== null);
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
					Nie udało się pobrać listy prac: <em>{this.fetchError!.toString()}</em>
				</span>
			}
		/>;
	}

	/** Download theses or set the error screen if an error occurred */
	private refreshTheses = flow(function*(this: ThesesApp) {
		try {
			const result = yield getThesesList(this.params, this.currentPage);
			if (this.currentPage === 1) {
				this.theses = result.theses;
			} else {
				this.theses = this.theses.concat(result.theses);
			}
			this.totalCount = result.total;
		} catch (err) {
			this.fetchError = err;
		}
	});

	private hasUnsavedChanges() {
		const { thesis } = this;
		return (
			thesis !== null &&
			!thesis.original.areValuesEqual(thesis.mutable!)
		);
	}

	private confirmDiscardChanges() {
		if (this.hasUnsavedChanges()) {
			const title = this.thesis!.mutable.title;
			return window.confirm(
				title
					? `Czy porzucić niezapisane zmiany w pracy "${title}"?`
					: "Czy porzucić niezapisane zmiany?"
			);
		}
		return true;
	}

	@action
	private onThesisSelected = (thesis: Thesis) => {
		if (!this.confirmDiscardChanges()) {
			return;
		}
		console.assert(
			this.theses.find(thesis.isEqual) != null,
			"Tried to select a nonexistent thesis",
		);
		this.workMode = ThesisWorkMode.Editing;
		this.thesis = compositeThesisForThesis(thesis);
	}

	/** Switch to the thesis at the specified offset from the current thesis */
	public switchWithOffset = (offset: number) => {
		const { selectedIdx, theses } = this;
		if (selectedIdx === -1) {
			return;
		}
		const target = selectedIdx + offset;
		if (!inRange(target, 0, theses.length - 1)) {
			return;
		}
		this.onThesisSelected(theses[target]);
	}

	// When modified in the Details subcomponent; we need to maintain
	// it on the main app state
	@action
	private onThesisModified = (thesis: Thesis) => {
		if (!this.thesis) {
			console.error("Modified nonexistent thesis");
			return;
		}
		this.thesis.mutable = thesis;
	}

	@action
	private setupForAddingThesis = () => {
		if (!canAddThesis(this.user)) {
			return;
		}
		const thesis = new Thesis();
		if (!canSetArbitraryAdvisor(this.user)) {
			thesis.advisor = this.user.user;
		}
		this.workMode = ThesisWorkMode.Adding;
		this.thesis = compositeThesisForThesis(thesis);
	}

	@action
	private resetChanges = () => {
		if (!this.hasUnsavedChanges()) {
			return;
		}
		this.thesis = compositeThesisForThesis(this.thesis!.original);
	}

	private preSaveChecks() {
		const { thesis, workMode } = this;
		if (thesis === null) {
			console.assert(false, "Tried to save thesis but none selected, this shouldn't happen");
			return false;
		}
		if (workMode === ThesisWorkMode.Viewing) {
			console.assert(false, "Tried to perform a save action when only viewing");
			return false;
		}
		if (!this.hasUnsavedChanges()) {
			console.assert(false, "save() called but no unsaved changes");
			return false;
		}
		return true;
	}

	private handlerForWorkMode = {
		[ThesisWorkMode.Adding]: this.addNewThesis,
		[ThesisWorkMode.Editing]: this.modifyExistingThesis,
	};

	private handleThesisSave = flow(function*(this: ThesesApp) {
		if (!this.preSaveChecks()) {
			return;
		}

		const { workMode } = this;

		this.applicationState = ApplicationState.PerformingBackendChanges;
		type NonViewModes = (ThesisWorkMode.Adding | ThesisWorkMode.Editing);
		const handler = this.handlerForWorkMode[workMode as NonViewModes];
		const id = yield handler.call(this);

		if (id === -1) {
			this.applicationState = ApplicationState.Normal;
			return;
		}
		this.currentPage = 1;
		yield this.refreshTheses();

		const toSelect = this.theses.find(t => t.id === id) || null;
		this.applicationState = ApplicationState.Normal;
		// no matter what the work mode was, if we have a thesis we end up in the edit view
		this.thesis = compositeThesisForThesis(toSelect);
	}).bind(this);

	private async modifyExistingThesis() {
		return this.performBackendAction(async thesis => {
			await saveModifiedThesis(thesis!.original, thesis!.mutable);
			return thesis!.original.id;
		});
	}

	private async addNewThesis() {
		return this.performBackendAction(thesis => {
			return saveNewThesis(thesis.mutable!);
		});
	}

	/**
	 * Perform the specified backend action and handle any errors
	 * @returns The ID of the thesis object the action was performed on
	 */
	private async performBackendAction(cb: (t: StateThesis) => Promise<number>) {
		const { thesis } = this;
		try {
			return await cb(thesis!);
		} catch (err) {
			window.alert(
				"Nie udało się zapisać pracy. Odśwież stronę i spróbuj jeszcze raz. " +
				"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów."
			);
			return -1;
		}
	}
}

function thesisIndexInList(thesis: Thesis | null, theses: Thesis[]) {
	return thesis
		? theses.findIndex(thesis.isEqual)
		: -1;
}

function indexToPage(index: number) {
	return Math.ceil(index / ROWS_PER_PAGE);
}

function compositeThesisForThesis(t: Thesis | null) {
	return t ? { original: t, mutable: clone(t) } : null;
}
