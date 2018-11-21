import * as React from "react";
import * as Mousetrap from "mousetrap";

import { Thesis } from "../types";
import { getThesesList, saveModifiedThesis } from "../backend_callers";
import { ThesisDetails } from "./ThesisDetails";
import { ApplicationState } from "../types/application_state";
import { ThesesTable } from "./ThesesTable";

type Props = {};

type State = {
	selectedThesis: Thesis | null;

	thesesList: Thesis[];
	applicationState: ApplicationState,
};

const initialState: State = {
	selectedThesis: null,

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

	public render() {
		console.warn("Main render");
		const mainComponent = <ThesesTable
			applicationState={this.state.applicationState}
			thesesList={this.state.thesesList}
			thesisForId={this.getThesisForId}
			onThesisClicked={this.onThesisClicked}
		/>;
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

	private getThesisForId = (
		id: number, theses: Thesis[] = this.state.thesesList,
	): Thesis | null => {
		return theses.find(t => t.id === id) || null;
	}

	private onThesisClicked = (thesis: Thesis) => {
		this.setState({ selectedThesis: thesis });
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
		// Mousetrap.bind("up", this.upArrow);
		// Mousetrap.bind("down", this.downArrow);
	}

	// private allowArrowSwitch() {
	// 	return (
	// 		document.activeElement === document.body
	// 	);
	// }
//
	// private upArrow = (e: ExtendedKeyboardEvent) => {
//
	// }
//
	// private downArrow = (e: ExtendedKeyboardEvent) => {
//
	// }
}
