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

	async componentDidMount() {
		this.setState({
			thesesList: await getThesesList(),
			applicationState: ApplicationState.Normal,
		});
	}

	public render() {
		console.warn("Main render");
		const { thesis } = this.state;
		const mainComponent = <ThesesTable
			applicationState={this.state.applicationState}
			thesesList={this.state.thesesList}
			thesisForId={this.getThesisForId}
			onThesisClicked={this.onThesisClicked}
			selectedThesis={thesis && thesis.original}
			isEditingThesis={this.thesisWasEdited()}
		/>;
		return thesis !== null
			? <>
				{mainComponent}
				<br />
				<hr />
				<ThesisDetails
					originalThesis={thesis.original}
					mutableThesis={thesis.mutable}
					onSaveRequested={this.handleThesisSave}
					isSaving={this.state.applicationState === ApplicationState.PerformingBackendChanges}
					shouldAllowSave={this.thesisWasEdited()}
				/>
			</>
			: mainComponent;
	}

	private onThesisClicked = (thesis: Thesis) => {
		this.setThesis(thesis);
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

	private thesisWasEdited() {
		const { thesis } = this.state;
		return (
			thesis !== null &&
			!thesis.original.areValuesEqual(thesis.mutable!)
		);
	}

	private handleThesisSave = async () => {
		const { thesis } = this.state;
		if (thesis === null) {
			console.warn("Tried to save thesis but none selected, this shouldn't happen");
			return;
		}
		console.assert(this.thesisWasEdited());

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
