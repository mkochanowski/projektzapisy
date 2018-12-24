import * as React from "react";
import * as Mousetrap from "mousetrap";
import { clone } from "lodash";

import { Thesis, UserType, AppUser } from "../types";
import {
	getThesesList, saveModifiedThesis, saveNewThesis,
	getCurrentUser, ThesisTypeFilter,
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
import {
	getProcessedTheses, SortColumn, SortDirection,
	clearFilterCache, ThesesProcessParams,
} from "./theses_store";

type State = {
	thesis: {
		original: Thesis,
		mutable: Thesis,
	} | null;
	thesisIdx: number;

	rawTheses: Thesis[];
	theses: Thesis[];
	applicationState: ApplicationState;
	fetchError: Error | null;
	wasTitleInvalid: boolean;
	workMode: ThesisWorkMode | null;
	user: AppUser;

	thesesParams: ThesesProcessParams;
};

const initialState: State = {
	thesis: null,
	thesisIdx: -1,

	rawTheses: [],
	theses: [],
	applicationState: ApplicationState.InitialLoading,
	fetchError: null,
	wasTitleInvalid: false,
	workMode: null,
	user: new AppUser({ user: { id: -1, display_name: "Unknown user" }, type: UserType.Student }),

	thesesParams: {
		type: ThesisTypeFilter.Default,
		title: "",
		advisor: "",
		sortColumn: SortColumn.None,
		sortDirection: SortDirection.Asc,
	},
};

const TopRowContainer = styled.div`
	display: flex;
	justify-content: space-between;
`;

export class ThesesApp extends React.Component<{}, State > {
	state = initialState;
	private oldOnBeforeUnload: ((this: WindowEventHandlers, ev: BeforeUnloadEvent) => any) | null = null;

	async componentDidMount() {
		const rawTheses = await this.safeGetRawTheses();
		this.setState({
			rawTheses,
			theses: getProcessedTheses(rawTheses, this.state.thesesParams),
			user: await getCurrentUser(),
			applicationState: ApplicationState.Normal,
		});
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

	private getNewStateForParams(params: Partial<ThesesProcessParams>): Partial<State> {
		const finalParams = Object.assign({}, this.state.thesesParams, params);
		const processed = getProcessedTheses(this.state.rawTheses, finalParams);
		return {
			thesesParams: finalParams,
			theses: processed,
			thesisIdx: thesisIndexInList(
				this.state.thesis && this.state.thesis.mutable, processed,
			),
		};
	}

	private updateFilters(title: string, advisor: string, type: ThesisTypeFilter) {
		const newState = this.getNewStateForParams({
			title: title, advisor: advisor, type: type,
		});
		clearFilterCache();
		this.setState(newState as State);
	}

	private onTypeFilterChanged = (value: ThesisTypeFilter) => {
		const { thesesParams } = this.state;
		this.updateFilters(thesesParams.title, thesesParams.advisor, value);
	}
	private onAdvisorFilterChanged = (value: string) => {
		const { thesesParams } = this.state;
		this.updateFilters(thesesParams.title, value.toLowerCase(), thesesParams.type);
	}
	private onTitleFilterChanged = (value: string) => {
		const { thesesParams } = this.state;
		this.updateFilters(value.toLowerCase(), thesesParams.advisor, thesesParams.type);
	}

	private renderTopRow() {
		const shouldShowNewBtn = canAddThesis(this.state.user);
		const { thesesParams } = this.state;
		return <TopRowContainer>
			<ListFilters
				onTypeChange={this.onTypeFilterChanged}
				typeValue={thesesParams.type}
				onAdvisorChange={this.onAdvisorFilterChanged}
				advisorValue={thesesParams.advisor}
				onTitleChange={this.onTitleFilterChanged}
				titleValue={thesesParams.title}
				enabled={this.state.applicationState === ApplicationState.Normal}
			/>
			{shouldShowNewBtn ? <AddNewButton onClick={this.setupForAddingThesis}/> : null}
		</TopRowContainer>;
	}

	private onSortChanged = (column: SortColumn, dir: SortDirection) => {
		const newState = this.getNewStateForParams({
			sortColumn: column, sortDirection: dir,
		});
		this.setState(newState as State);
	}

	private renderThesesList() {
		return <ThesesTable
			applicationState={this.state.applicationState}
			theses={this.state.theses}
			selectedIdx={this.state.thesisIdx}
			sortColumn={this.state.thesesParams.sortColumn}
			sortDirection={this.state.thesesParams.sortDirection}
			isEditingThesis={this.hasUnsavedChanges()}
			onThesisSelected={this.onThesisSelected}
			switchToThesisWithOffset={this.switchWithOffset}
			onSortChanged={this.onSortChanged}
		/>;
	}

	private renderThesesDetails() {
		return <ThesisDetails
			thesis={this.state.thesis!.mutable}
			thesesList={this.state.rawTheses}
			isSaving={this.state.applicationState === ApplicationState.PerformingBackendChanges}
			hasUnsavedChanges={this.hasUnsavedChanges()}
			mode={this.state.workMode!}
			user={this.state.user}
			onSaveRequested={this.handleThesisSave}
			onThesisModified={this.onThesisModified}
		/>;
	}

	public render() {
		if (this.state.fetchError) {
			return this.renderErrorScreen();
		}
		const { thesis } = this.state;
		const mainComponent = <>
			{this.renderTopRow()}
			<br />
			{this.renderThesesList()}
		</>;
		if (thesis !== null) {
			console.assert(this.state.workMode !== null);
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
					Nie udało się pobrać listy prac: <em>{this.state.fetchError!.toString()}</em>
				</span>
			}
		/>;
	}

	// properly typing setState in TS is nontrivial because of a peculiarity
	// of the type system: there is no distinction between absent keys
	// and keys with `undefined` as their value; for this reason the React
	// .d.ts files hack around using Pick<State, K>, but this doesn't work
	// for multiple levels (i.e. if this function's state argument has the same
	// type as React's setState argument definition, it will not work anyway)
	// for this reason we simply use Partial<State> and cast it later
	private setStateWithNewThesis(state: Partial<State>, t: Thesis | null) {
		const finalState = Object.assign({
			thesis: t ? { original: t, mutable: clone(t) } : null,
			thesisIdx: thesisIndexInList(t, state.theses || this.state.theses)
		}, state);
		this.setState(finalState as State);
	}

	private async safeGetRawTheses() {
		try {
			return await getThesesList();
		} catch (err) {
			this.setState({ fetchError: err });
			return [];
		}
	}

	private hasUnsavedChanges() {
		const { thesis } = this.state;
		return (
			thesis !== null &&
			!thesis.original.areValuesEqual(thesis.mutable!)
		);
	}

	private confirmDiscardChanges() {
		if (this.hasUnsavedChanges()) {
			const title = this.state.thesis!.mutable.title;
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
		console.assert(
			this.state.rawTheses.find(thesis.isEqual) != null,
			"Tried to select a nonexistent thesis",
		);
		this.setStateWithNewThesis({ workMode: ThesisWorkMode.Editing }, thesis);
	}

	public switchWithOffset = (offset: number) => {
		const { thesisIdx, theses } = this.state;
		if (thesisIdx === -1) {
			return;
		}
		const target = thesisIdx + offset;
		if (!inRange(target, 0, theses.length - 1)) {
			return;
		}
		this.onThesisSelected(theses[target]);
	}

	// When modified in the Details subcomponent; we need to maintain
	// it on the main app state
	private onThesisModified = (thesis: Thesis) => {
		this.setState({
			thesis: {
				original: this.state.thesis!.original,
				mutable: thesis,
			}
		});
	}

	private setupForAddingThesis = () => {
		if (!canAddThesis(this.state.user)) {
			return;
		}
		const thesis = new Thesis();
		if (!canSetArbitraryAdvisor(this.state.user)) {
			thesis.advisor = this.state.user.user;
		}
		this.setStateWithNewThesis({
			workMode: ThesisWorkMode.Adding
		}, thesis);
	}

	private resetChanges = () => {
		if (!this.hasUnsavedChanges()) {
			return;
		}
		this.setStateWithNewThesis({}, this.state.thesis!.original);
	}

	private handlerForWorkMode = {
		[ThesisWorkMode.Adding]: this.addNewThesis,
		[ThesisWorkMode.Editing]: this.modifyExistingThesis,
	};

	private handleThesisSave = async () => {
		const { thesis, workMode } = this.state;
		if (thesis === null) {
			console.warn("Tried to save thesis but none selected, this shouldn't happen");
			return;
		}
		if (workMode === null) {
			console.assert(false, "Tried to perform a save action without a work mode");
			return;
		}
		console.assert(this.hasUnsavedChanges());

		this.setState({ applicationState: ApplicationState.PerformingBackendChanges });
		const handler = this.handlerForWorkMode[workMode];
		const id = await handler.call(this);

		if (id === -1) {
			this.setState({ applicationState: ApplicationState.Normal });
			return;
		}
		// Re-fetch everything
		// this might seem pointless but as we don't currently have any
		// backend synchronization this is the only chance to refresh
		// everything
		const newList = await this.safeGetRawTheses();
		// We'll want to find the thesis we just saved
		// Note that it _could_ technically be absent from the new list
		// but the odds are absurdly low (it would have to be deleted by someone
		// else or the admin in the time between those two requests above)
		const freshThesisInstance = newList.find(t => t.id === id) || null;
		const newState: Partial<State> = {
			rawTheses: newList,
			theses: getProcessedTheses(newList, this.state.thesesParams),
			applicationState: ApplicationState.Normal,
			// no matter what the work mode was, if we have a thesis we end up in the edit view
			workMode: freshThesisInstance ? ThesisWorkMode.Editing : null,
		};
		this.setStateWithNewThesis(newState, freshThesisInstance);
	}

	private async modifyExistingThesis() {
		const { thesis } = this.state;
		try {
			await saveModifiedThesis(thesis!.original, thesis!.mutable);
			return thesis!.original.id;
		} catch (err) {
			window.alert(
				"Nie udało się zapisać pracy. Odśwież stronę i spróbuj jeszcze raz. " +
				"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów."
			);
			return -1;
		}
	}

	private async addNewThesis() {
		const { thesis } = this.state;
		try {
			return await saveNewThesis(thesis!.mutable);
		} catch (err) {
			window.alert(
				"Nie udało się dodać pracy. Odśwież stronę i spróbuj jeszcze raz. " +
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
