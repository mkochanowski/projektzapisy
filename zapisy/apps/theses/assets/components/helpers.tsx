import { confirmAlert } from "react-confirm-alert";

export type ConfirmationDialogProps = {
	title?: string;
	message: string;
	yesText: string;
	noText: string;
};

/**
 * Displays a confirmation dialog with the given parameters.
 * @returns A promise that resolves to the user's choice
 */
export function confirmationDialog(props: ConfirmationDialogProps): Promise<boolean> {
	const final = Object.assign({
		title: "",
	}, props);
	return new Promise((resolve) => {
		confirmAlert({
			title: final.title,
			message: final.message,
			buttons: [
				{
					label: final.yesText,
					onClick: () => resolve(true),
				},
				{
					label: final.noText,
					onClick: () => resolve(false),
				}
			],
		});
	});
}
