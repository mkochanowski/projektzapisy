import * as React from "react";
import { confirmAlert } from "react-confirm-alert";
import styled from "styled-components";
import * as Mousetrap from "mousetrap";

import "./dialog_styles.less";

const DialogContainer = styled.div`
	font-family: Arial, Helvetica, sans-serif;
	width: 400px;
	padding: 30px;
	text-align: left;
	background: #fff;
	border-radius: 10px;
	box-shadow: 0 20px 75px rgba(0, 0, 0, 0.13);
	color: #666;

	& > h2 {
		margin-top: -10px;
		margin-bottom: 15px;
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

const SafeButton = styled(BaseButton)`
	color: #6f6f6f;
	&:hover {
		color: #6f6f6f;
		filter: brightness(0.9);
	}
`;

const ConfirmButton = styled(BaseButton)`
	color: #fff;
	background-color: #337ab7;
	border-color: #2e6da4;
	font-size: 14px;
	min-width: 100px;
	&:hover {
		color: #fff;
		filter: brightness(1.1);
	}
`;

const Buttons = styled.div`
	margin-top: 20px;
`;

export type ConfirmationProps = {
	title?: string;
	message: string | JSX.Element;
	yesText: string;
	noText: string;
};

type ConfirmDialogUIProps = ConfirmationProps & {
	closeUI: () => void;
	resolve: (r: boolean) => void;
};

class ConfirmDialogUI extends React.PureComponent<ConfirmDialogUIProps> {
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
			{props.title ? <h2>{props.title}</h2> : null}
			{props.message}
			<Buttons>
				<SafeButton type="button" className="btn" onClick={this.onNo}>
					{props.noText}
				</SafeButton>
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
export function confirmationDialog(props: ConfirmationProps): Promise<boolean> {
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

export type MessageProps = {
	title?: string;
	message: string | JSX.Element;
	buttonText?: string;
};

type MessageDialogUIProps = MessageProps & {
	closeUI: () => void;
};

const OkButtonContainer = styled(Buttons)`
	width: 100%;
	text-align: center;
`;

class MessageDialogUI extends React.PureComponent<MessageDialogUIProps> {
	public componentDidMount() {
		Mousetrap.bindGlobal(["enter", "esc"], this.close);
	}
	public componentWillUnmount() {
		Mousetrap.unbindGlobal(["enter", "esc"]);
	}

	private close = () => {
		this.props.closeUI();
	}

	public render() {
		const { props } = this;
		return <DialogContainer>
			{props.title ? <h2>{props.title}</h2> : null}
			{props.message}
			<OkButtonContainer>
				<ConfirmButton type="button" className="btn" onClick={this.close}>
					{props.buttonText}
				</ConfirmButton>
			</OkButtonContainer>
		</DialogContainer>;
	}
}

export function showErrorMessage(props: MessageProps) {
	confirmAlert({
		message: "",
		title: "",
		customUI: ({ onClose }: any) => (
			<MessageDialogUI
				closeUI={onClose}
				title={props.title || "Błąd"}
				message={props.message}
				buttonText={props.buttonText || "OK"}
			/>
		)
	});
}

const ThesisTitle = styled.span`
	font-style: italic;
`;
export function formatTitle(title: string) {
	return <ThesisTitle>{title}</ThesisTitle>;
}
