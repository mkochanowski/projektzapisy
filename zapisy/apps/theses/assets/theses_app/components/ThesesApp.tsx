import * as React from "react";

import * as Mousetrap from "mousetrap";

import { Thesis, ThesisStatus, ThesisKind } from "../types";
import { TopFilters } from "./TopFilters";
import { ThesisTypeFilter, getThesesList, saveModifiedThesis } from "../backend_callers";
import { ThesisDetails } from "./ThesisDetails";
import { ApplicationState } from "../types/application_state";


type Props = {};

type State = {
	selectedThesis: Thesis | null;
	currentTypeFilter: ThesisTypeFilter;
	currentTitleFilter: string;
	currentAdvisorFilter: string;

	thesesList: Thesis[];
	applicationState: ApplicationState,
};

const initialState: State = {
	selectedThesis: null,

	currentTypeFilter: ThesisTypeFilter.Default,
	currentTitleFilter: "",
	currentAdvisorFilter: "",

	thesesList: [],
	applicationState: ApplicationState.InitialLoading,
};



export class ThesesApp extends React.Component<Props, State> {
	state = initialState;

	async componentDidMount() {
		this.installKeyHandler();
		this.setState({
			thesesList: await getThesesList(),
			applicationState: ApplicationState.Normal,
		});
	}

	componentWillUnmount() {
		this.uninstallKeyHandler();
	}

	private setStateAsync<K extends keyof State>(partialState: Pick<State, K>): Promise<void> {
		return new Promise((resolve, _) => {
			this.setState(partialState, resolve);
		});
	}

	private renderTopFilters() {
		return <TopFilters
			onTypeChange={this.onTypeFilterChanged}
			typeValue={this.state.currentTypeFilter}
			onAdvisorChange={this.onAdvisorFilterChanged}
			advisorValue={this.state.currentAdvisorFilter}
			onTitleChange={this.onTitleFilterChanged}
			titleValue={this.state.currentTitleFilter}
			enabled={this.state.applicationState === ApplicationState.Normal}
		/>;
	}

	private getThesisForId(id: number, theses: Thesis[] = this.state.thesesList): Thesis | null {
		return theses.find(t => t.id === id) || null;
	}

	private onRowClick = (row: any, _e: MouseEvent) => {
		const data: GriddleThesisData = row.props.data;
		const thesis = this.getThesisForId(data.id);
		if (!thesis) {
			console.warn(`[Table onclick] Griddle had bad thesis ID ${data.id}`);
		}
		this.setState({ selectedThesis: thesis });
	}

	public render() {
		console.warn("Main render");
		const mainComponent = (
			<>
				{this.renderTopFilters()}
				<br />
				{this.renderThesesList()}
			</>
		);
		const { selectedThesis } = this.state;
		return selectedThesis !== null
			? <>
				{mainComponent}
				<br />
				<hr />
				<ThesisDetails
					selectedThesis={selectedThesis}
					onSaveRequested={this.handleThesisSave}
					isSaving={this.state.applicationState === ApplicationState.PerformingBackendChanges}
				/>
			</>
			: mainComponent;
	}

	private handleThesisSave = async (modifiedThesis: Thesis) => {
		const { selectedThesis } = this.state;
		if (selectedThesis === null) {
			console.warn("Tried to save thesis but none selected, this shouldn't happen");
			return;
		}
		this.setState({ applicationState: ApplicationState.PerformingBackendChanges });
		const oldSelectedThesisId = selectedThesis.id;
		try {
			await saveModifiedThesis(selectedThesis, modifiedThesis);
		} catch (err) {
			alert(
				"Nie udało się zapisać pracy. Spróbuj jeszcze raz. " +
				"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów"
			);
			return;
		}
		// This could theoretically be null if someone deletes what we've just saved
		// slim chance but who knows
		const newList = await getThesesList();
		const newThesisInstance = this.getThesisForId(oldSelectedThesisId, newList);
		this.setState({
			thesesList: newList,
			applicationState: ApplicationState.Normal,
			selectedThesis: newThesisInstance,
		});
	}

	
	private uninstallKeyHandler() {
		Mousetrap.unbind(["up", "down"]);
	}

	private installKeyHandler() {
		Mousetrap.bind("up", this.upArrow);
		Mousetrap.bind("down", this.downArrow);
	}

	private allowArrowSwitch() {
		return (
			document.activeElement === document.body &&

	}

	private upArrow = (e : ExtendedKeyboardEvent) => {

	}
}

function isThesisAvailable(thesis: Thesis): boolean {
	return (
		thesis.status !== ThesisStatus.InProgress &&
		thesis.status !== ThesisStatus.Defended &&
		!thesis.reserved
	);
}

function thesisMatchesType(thesis: Thesis, type: ThesisTypeFilter) {
	switch (type) {
		case ThesisTypeFilter.All: return true;
		case ThesisTypeFilter.AllCurrent: return isThesisAvailable(thesis);
		case ThesisTypeFilter.Masters: return thesis.kind === ThesisKind.Masters;
		case ThesisTypeFilter.Engineers: return thesis.kind === ThesisKind.Engineers;
		case ThesisTypeFilter.Bachelors: return thesis.kind === ThesisKind.Bachelors;
		case ThesisTypeFilter.BachelorsISIM: return thesis.kind === ThesisKind.Isim;
		case ThesisTypeFilter.AvailableMasters:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Masters;
		case ThesisTypeFilter.AvailableEngineers:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Engineers;
		case ThesisTypeFilter.AvailableBachelors:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Bachelors;
		case ThesisTypeFilter.AvailableBachelorsISIM:
			return isThesisAvailable(thesis) && thesis.kind === ThesisKind.Isim;
	}
}
