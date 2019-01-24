import { observable, action, flow, computed } from "mobx";
import { cloneDeep } from "lodash";

import { Thesis } from "../thesis";
import { ThesisEmptyTitle } from "../errors";
import { saveModifiedThesis, saveNewThesis, deleteThesis } from "../backend_callers";
import { ThesisWorkMode, ApplicationState } from "../app_types";
import { AppMode } from "./app_mode";
import { List } from "./theses_list";
import { Users } from "./users";
import { canSetArbitraryAdvisor } from "../permissions";
import { Employee } from "../users";

/** The currently selected thesis */
type CompositeThesis = {
	/** Its original, unchanged version */
	original: Thesis;
	/** And the version the user is modifying */
	modified: Thesis;
};

class C {
	@observable thesis: CompositeThesis | null = null;

	/**
	 * Set the specified thesis as selected
	 * @param thesis The thesis to select; must be in the local theses list
	 */
	@action
	public selectThesis(thesis: Thesis | null) {
		if (thesis) {
			console.assert(
				List.indexOfThesis(thesis) !== -1,
				"Tried to select a nonexistent thesis"
			);
		}
		this.thesis = compositeThesisForThesis(thesis);
		AppMode.workMode = thesis ? ThesisWorkMode.Editing : ThesisWorkMode.Viewing;
	}

	/** The position of the currently selected thesis in the list */
	@computed
	public get selectedIdx() {
		const { thesis } = this;
		return thesis ? List.indexOfThesis(thesis.original) : -1;
	}

	/** Determine whether we have a thesis being modified and if so,
	 * whether it's different from the original one
	 */
	@computed
	public get hasUnsavedChanges() {
		const { thesis } = this;
		return (
			thesis !== null &&
			!thesis.original.areValuesEqual(thesis.modified)
		);
	}

	/**
	 * Update the modified thesis instance (it's an immutable object, a new instance
	 * must be set)
	 * @param thesis The new modified instance
	 */
	@action
	public updateModifiedThesis(thesis: Thesis) {
		if (!this.thesis) {
			console.error("Modified nonexistent thesis");
			return;
		}
		this.thesis.modified = thesis;
	}

	/**
	 * Set the specified thesis as active and switch to adding mode
	 * @param thesis The thesis we'll be adding
	 */
	@action
	public setupForNewThesis() {
		AppMode.workMode = ThesisWorkMode.Adding;
		const empUser = Users.currentUser.person as Employee;
		const thesis = new Thesis();
		if (!canSetArbitraryAdvisor()) {
			thesis.advisor = empUser;
		}
		this.thesis = compositeThesisForThesis(thesis);
	}

	/**
	 * Discard all changes in the modified instance, resetting it to original
	 */
	@action
	public resetModifiedThesis() {
		console.assert(this.thesis != null);
		this.thesis = compositeThesisForThesis(this.thesis!.original);
	}

	public delete = flow(function*(this: C) {
		try {
			if (this.thesis == null) {
				console.assert(false, "Cannot delete thesis when not selected");
				return;
			}
			if (AppMode.workMode !== ThesisWorkMode.Editing) {
				console.assert(false, "Cannot delete when not editing");
				return;
			}
			AppMode.applicationState = ApplicationState.Saving;
			yield deleteThesis(this.thesis.original);
			yield List.reloadTheses();
			this.selectThesis(null);
		} finally {
			AppMode.applicationState = ApplicationState.Normal;
		}
	});

	private preSaveAsserts() {
		const { thesis } = this;
		if (thesis === null) {
			console.assert(false, "Tried to save thesis but none selected, this shouldn't happen");
			return false;
		}
		const { workMode } = AppMode;
		if (workMode === ThesisWorkMode.Viewing) {
			console.assert(false, "Tried to perform a save action when only viewing");
			return false;
		}
		if (!this.hasUnsavedChanges) {
			console.assert(false, "save() called but no unsaved changes");
			return false;
		}
		if (AppMode.isPerformingBackendOp()) {
			console.assert(false, "Called save() but we're already doing something backend-related");
			return false;
		}
		return true;
	}

	private performPreSaveChecks() {
		const { modified } = this.thesis!;
		const trimmedTitle = modified.title.trim();
		if (!trimmedTitle) {
			throw new ThesisEmptyTitle();
		}
	}

	private static handlerForWorkMode = {
		[ThesisWorkMode.Adding]: addNewThesis,
		[ThesisWorkMode.Editing]: modifyExistingThesis,
	};

	/**
	 * Save the currently selected thesis. It is an error to call this
	 * if there are no unsaved changes.
	 */
	public save = flow(function*(this: C) {
		try {
			if (!this.preSaveAsserts()) {
				return;
			}
			this.performPreSaveChecks();

			const thesis = this.thesis!;
			const { workMode } = AppMode;

			AppMode.applicationState = ApplicationState.Saving;
			type NonViewModes = (ThesisWorkMode.Adding | ThesisWorkMode.Editing);
			const handler = C.handlerForWorkMode[workMode as NonViewModes];

			const id = yield handler(thesis);

			// Reload without losing the current position
			yield List.reloadTheses();

			const toSelect = List.getThesisById(id);
			this.selectThesis(toSelect);
		} finally {
			AppMode.applicationState = ApplicationState.Normal;
		}
	});
}

async function modifyExistingThesis(thesis: CompositeThesis) {
	await saveModifiedThesis(thesis.original, thesis.modified);
	return thesis!.original.id;
}

function addNewThesis(thesis: CompositeThesis) {
	return saveNewThesis(thesis.modified);
}

function compositeThesisForThesis(t: Thesis | null) {
	return t ? { original: t, modified: cloneDeep(t) } : null;
}

export const ThesisEditing = new C();
