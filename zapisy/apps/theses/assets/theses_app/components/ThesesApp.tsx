import * as React from "react";
import * as Mousetrap from "mousetrap";
import { clone } from "lodash";

import { Thesis } from "../types";
import { getThesesList, saveModifiedThesis, saveNewThesis } from "../backend_callers";
import { ThesisDetails } from "./ThesisDetails";
import { ApplicationState, ThesisWorkMode } from "../types/misc";
import { ThesesTable } from "./ThesesTable";
import { ErrorBox } from "./ErrorBox";

type Props = {};

type State = {
	thesis: {
		original: Thesis,
		mutable: Thesis,
	} | null;

	thesesList: Thesis[];
	applicationState: ApplicationState;
	fetchError: Error | null;
	wasTitleInvalid: boolean;
	workMode: ThesisWorkMode | null;
};

const initialState: State = {
	thesis: null,

	thesesList: [],
	applicationState: ApplicationState.InitialLoading,
	fetchError: null,
	wasTitleInvalid: false,
	workMode: null,
};

export class ThesesApp extends React.Component<Props, State> {
	state = initialState;
	private oldOnBeforeUnload: ((this: Window, ev: BeforeUnloadEvent) => any) | null = null;

	async componentDidMount() {
		this.setState({
			thesesList: await this.safeGetTheses(),
			applicationState: ApplicationState.Normal,
		});
		this.oldOnBeforeUnload = window.onbeforeunload;
		window.onbeforeunload = this.confirmUnload;
		Mousetrap.bind("ctrl+m", this.setupForNewThesis);
	}

	componentWillUnmount() {
		window.onbeforeunload = this.oldOnBeforeUnload;
		Mousetrap.unbind("ctrl+m");
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
		if (this.state.fetchError) {
			return this.renderErrorScreen();
		}
		console.warn("Main render");
		const { thesis } = this.state;
		const mainComponent = <ThesesTable
			applicationState={this.state.applicationState}
			thesesList={this.state.thesesList}
			onThesisSelected={this.onThesisSelected}
			selectedThesis={thesis && thesis.original}
			isEditingThesis={this.hasUnsavedChanges()}
		/>;
		if (thesis !== null) {
			console.assert(this.state.workMode !== null);
			return <>
				{mainComponent}
				<br />
				<hr />
				<ThesisDetails
					thesis={thesis.mutable}
					thesesList={this.state.thesesList}
					onSaveRequested={this.handleThesisSave}
					isSaving={this.state.applicationState === ApplicationState.PerformingBackendChanges}
					shouldAllowSave={this.hasUnsavedChanges()}
					onThesisModified={this.onThesisModified}
					mode={this.state.workMode!}
				/>
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

	private async safeGetTheses() {
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
				`Czy porzucić niezapisane zmiany w pracy "${title}"?`
			);
		}
		return true;
	}

	private onThesisSelected = (thesis: Thesis) => {
		if (!this.confirmDiscardChanges()) {
			return;
		}
		console.assert(
			this.state.thesesList.find(thesis.isEqual) != null,
			"Tried to select a nonexistent thesis",
		);
		this.setActiveThesis(thesis);
		this.setState({ workMode: ThesisWorkMode.Editing });
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

	private setActiveThesis(t: Thesis | null) {
		this.setState({
			thesis: t ? { original: t, mutable: clone(t) } : null,
		});
	}

	private setupForNewThesis = () => {
		const thesis = new Thesis();
		this.setActiveThesis(thesis);
		this.setState({ workMode: ThesisWorkMode.Adding });
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

		if (id === null) {
			this.setState({ applicationState: ApplicationState.Normal });
			return;
		}
		// Re-fetch everything
		// this might seem pointless but as we don't currently have any
		// backend synchronization this is the only chance to refresh
		// everything
		const newList = await this.safeGetTheses();
		// We'll want to find the thesis we just saved
		// Note that it _could_ technically be absent from the new list
		// but the odds are absurdly low (it would have to be deleted by someone
		// else or the admin in the time between those two requests above)
		const freshThesisInstance = newList.find(t => t.id === id) || null;
		this.setState({ thesesList: newList });
		this.setActiveThesis(freshThesisInstance);
		this.setState({ applicationState: ApplicationState.Normal });

		// no matter what the work mode was, if we have a thesis we end up in the edit view
		this.setState({ workMode: freshThesisInstance ? ThesisWorkMode.Editing : null });
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
			return null;
		}
	}

	private async addNewThesis() {
		const { thesis } = this.state;
		try {
			await saveNewThesis(thesis!.mutable);
			return -1;
		} catch (err) {
			window.alert(
				"Nie udało się dodać pracy. Odśwież stronę i spróbuj jeszcze raz. " +
				"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów."
			);
			return null;
		}
	}
}
