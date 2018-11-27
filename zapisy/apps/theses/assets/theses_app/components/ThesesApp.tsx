import * as React from "react";
import { clone } from "lodash";

import { Thesis } from "../types";
import { getThesesList, saveModifiedThesis } from "../backend_callers";
import { ThesisDetails } from "./ThesisDetails";
import { ApplicationState } from "../types/application_state";
import { ThesesTable } from "./ThesesTable";

type Props = {};

type State = {
	thesis: {
		original: Thesis,
		mutable: Thesis,
	} | null;

	thesesList: Thesis[];
	applicationState: ApplicationState,
};

const initialState: State = {
	thesis: null,

	thesesList: [],
	applicationState: ApplicationState.InitialLoading,
};

export class ThesesApp extends React.Component<Props, State> {
	state = initialState;
	private oldOnBeforeUnload: ((this: Window, ev: BeforeUnloadEvent) => any) | null = null;

	async componentDidMount() {
		this.setState({
			thesesList: await getThesesList(),
			applicationState: ApplicationState.Normal,
		});
		this.oldOnBeforeUnload = window.onbeforeunload;
		window.onbeforeunload = this.confirmUnload;
	}

	componentWillUnmount() {
		window.onbeforeunload = this.oldOnBeforeUnload;
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

	public render() {
		console.warn("Main render");
		const { thesis } = this.state;
		const mainComponent = <ThesesTable
			applicationState={this.state.applicationState}
			thesesList={this.state.thesesList}
			thesisForId={this.getThesisForId}
			onThesisSelected={this.onThesisSelected}
			selectedThesis={thesis && thesis.original}
			isEditingThesis={this.hasUnsavedChanges()}
		/>;
		return thesis !== null
			? <>
				{mainComponent}
				<br />
				<hr />
				<ThesisDetails
					thesis={thesis.mutable}
					onSaveRequested={this.handleThesisSave}
					isSaving={this.state.applicationState === ApplicationState.PerformingBackendChanges}
					shouldAllowSave={this.hasUnsavedChanges()}
					onThesisModified={this.onThesisModified}
				/>
			</>
			: mainComponent;
	}

	private hasUnsavedChanges() {
		const { thesis } = this.state;
		return (
			thesis !== null &&
			!thesis.original.areValuesEqual(thesis.mutable!)
		);
	}

	private onThesisSelected = (thesis: Thesis) => {
		if (this.hasUnsavedChanges()) {
			const title = this.state.thesis!.mutable.title;
			if (!confirmDiscardChanges(title)) {
				return;
			}
		}
		console.assert(
			this.state.thesesList.find(thesis.isEqual) != null,
			"Tried to select a nonexistent thesis",
		);
		this.setActiveThesis(thesis);
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

	private getThesisForId = (
		id: number, theses: Thesis[] = this.state.thesesList,
	): Thesis | null => {
		return theses.find(t => t.id === id) || null;
	}

	private setActiveThesis(t: Thesis | null) {
		this.setState({
			thesis: t ? { original: t, mutable: clone(t) } : null,
		});
	}

	private handleThesisSave = async () => {
		const { thesis } = this.state;
		if (thesis === null) {
			console.warn("Tried to save thesis but none selected, this shouldn't happen");
			return;
		}
		console.assert(this.hasUnsavedChanges());

		this.setState({ applicationState: ApplicationState.PerformingBackendChanges });
		try {
			await saveModifiedThesis(thesis.original, thesis.mutable);
		} catch (err) {
			alert(
				"Nie udało się zapisać pracy. Spróbuj jeszcze raz. " +
				"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów"
			);
			return;
		}
		// Re-fetch everything
		// this might seem pointless but as we don't currently have any
		// backend synchronization this is the only chance to refresh
		// everything
		const newList = await getThesesList();
		// We'll want to find the thesis we just saved
		// Note that it _could_ technically be absent from the new list
		// but the odds are absurdly low (it would have to be deleted by someone
		// else or the admin in the time between those two requests above)
		const freshThesisInstance = newList.find(thesis.original.isEqual) || null;
		this.setState({ thesesList: newList });
		this.setActiveThesis(freshThesisInstance);
		this.setState({ applicationState: ApplicationState.Normal });
	}
}

function confirmDiscardChanges(thesisTitle: string) {
	return window.confirm(
		`Czy porzucić niezapisane zmiany w pracy "${thesisTitle}"?`
	);
}
