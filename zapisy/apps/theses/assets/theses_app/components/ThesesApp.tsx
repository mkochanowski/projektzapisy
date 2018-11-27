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
			// preventDefault() is what the spec says, in practice some
			// browsers like returnValue to be set
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
			onThesisSelected={this.onThesisClicked}
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

	private onThesisClicked = (thesis: Thesis) => {
		if (this.hasUnsavedChanges()) {
			const title = this.state.thesis!.mutable.title;
			if (!confirmDiscardChanges(title)) {
				return;
			}
		}
		this.setThesis(thesis);
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

	private setThesis(t: Thesis) {
		console.assert(
			this.state.thesesList.find(t.isEqual) != null,
			"Trying to set a nonexistent thesis",
		);
		this.setState({
			thesis: { original: t, mutable: clone(t) },
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
		// Update the list to contain the new thesis
		const oldIdx = this.state.thesesList.findIndex(
			t => t.id === thesis.original.id
		);
		console.assert(oldIdx !== -1);
		this.state.thesesList[oldIdx] = thesis.mutable;
		this.setThesis(thesis.mutable);
		this.setState({
			applicationState: ApplicationState.Normal,
		});
	}
}

function confirmDiscardChanges(thesisTitle: string) {
	return window.confirm(
		`Czy porzucić niezapisane zmiany w pracy "${thesisTitle}"?`
	);
}
