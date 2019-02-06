import * as React from "react";
import { confirmAlert } from "react-confirm-alert";
import styled from "styled-components";
import * as Mousetrap from "mousetrap";

const DialogContainer = styled.div`
	font-family: Arial, Helvetica, sans-serif;
	width: 400px;
	padding: 30px;
	text-align: left;
	background: #fff;
	border-radius: 10px;
	box-shadow: 0 20px 75px rgba(0, 0, 0, 0.13);
	color: #666;

	& > h1 {
		margin-top: 0;
	}
`;

const BaseButton = styled.button`
	text-shadow: none;
	background-image: none;
`;

const DangerButton = styled(BaseButton)`
	color: #fff;
	background-color: #d9534f;
	border-color: #d43f3a;
	margin-left: 10px;

	&:hover {
		color: #fff;
		filter: brightness(1.1);
	}
`;

const ConfirmButton = styled(BaseButton)`
	color: #6f6f6f;
	&:hover {
		color: #6f6f6f;
		filter: brightness(0.9);
	}
`;

const Buttons = styled.div`
	margin-top: 20px;
`;

export type ConfirmationDialogProps = {
	title?: string;
	message: string | JSX.Element;
	yesText: string;
	noText: string;
};

type CustomDialogUIProps = ConfirmationDialogProps & {
	closeUI: () => void;
	resolve: (r: boolean) => void;
};

class ConfirmDialogUI extends React.PureComponent<CustomDialogUIProps> {
	public componentDidMount() {
		Mousetrap.bindGlobal("enter", this.onYes);
		Mousetrap.bindGlobal("esc", this.onNo);
	}

	public componentWillUnmount() {
		Mousetrap.unbindGlobal(["enter", "esc"]);
	}

	private finishWith(val: boolean) {
		this.props.resolve(val);
		this.props.closeUI();
	}

	private onNo = () => this.finishWith(false);
	private onYes = () => this.finishWith(true);

	public render() {
		const { props } = this;
		return <DialogContainer>
			{props.message}
			<Buttons>
				<ConfirmButton type="button" className="btn" onClick={this.onNo}>
					{props.noText}
				</ConfirmButton>
				<DangerButton type="button" className="btn" onClick={this.onYes}>
					{props.yesText}
				</DangerButton>
			</Buttons>
		</DialogContainer>;
	}
}

/**
 * Displays a confirmation dialog with the given parameters.
 * @returns A promise that resolves to the user's choice
 */
export function confirmationDialog(props: ConfirmationDialogProps): Promise<boolean> {
	return new Promise((resolve) => {
		confirmAlert({
			title: "",
			message: "",
			customUI: ({ onClose }: any) => (
				<ConfirmDialogUI
					closeUI={onClose}
					resolve={resolve}
					{...props}
				/>
			)
		});
	});
}

export function showErrorMessage(msg: string) {
	confirmAlert({
		title: "Błąd",
		message: msg,
		buttons: [{ label: "OK" }],
	});
}

const ThesisTitle = styled.span`
	font-style: italic;
`;
export function formatTitle(title: string) {
	return <ThesisTitle>{title}</ThesisTitle>;
}
