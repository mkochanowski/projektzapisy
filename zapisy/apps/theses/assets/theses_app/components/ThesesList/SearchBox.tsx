import * as React from "react";

type Props = {
	label: string;
	onChanged: (newString: string) => void;
};

export class SearchBox extends React.Component<Props> {
	render() {
		return [
			<span key="searchbox_label">{this.props.label} </span>,
			<input
				key="searchbox_box"
				onInput={ev => this.props.onChanged((ev.target as HTMLInputElement).value)}
				type={"text"}
				style={{
					border: "1px solid black",
					borderRadius: "15px",
					height: "12px",
					width: "130px",
					backgroundClip: "padding-box",
				}}
			/>,
		];
	}
}
