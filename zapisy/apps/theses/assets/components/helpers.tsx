import { confirmAlert } from "react-confirm-alert";

export type ConfirmationDialogProps = {
	title?: string;
	message: string;
	yesText: string;
	noText: string;
};

export function confirmationDialog(props: ConfirmationDialogProps) {
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
