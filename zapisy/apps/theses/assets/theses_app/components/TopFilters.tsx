import * as React from "react";

import { ThesisTypeFilter } from "../backend_callers";
import { GenericSelect } from "./GenericSelect";

const typefilterInfos = [
	{ val: ThesisTypeFilter.AllCurrent, displayName: "Wszystkie aktualne" },
	{ val: ThesisTypeFilter.All, displayName: "Wszystkie" },
	{ val: ThesisTypeFilter.Masters, displayName: "Magisterskie" },
	{ val: ThesisTypeFilter.Engineers, displayName: "Inżynierskie" },
	{ val: ThesisTypeFilter.Bachelors, displayName: "Licencjackie" },
	{ val: ThesisTypeFilter.BachelorsISIM, displayName: "Licencjackie ISIM" },
	{ val: ThesisTypeFilter.AvailableMasters, displayName: "Magisterskie - dostępne" },
	{ val: ThesisTypeFilter.AvailableEngineers, displayName: "Inżynierskie - dostępne" },
	{ val: ThesisTypeFilter.AvailableBachelors, displayName: "Licencjackie - dostępne" },
	{ val: ThesisTypeFilter.AvailableBachelorsISIM, displayName: "Licencjackie ISIM - dostępne" },
];

type State = {
	typeValue: ThesisTypeFilter;
	advisorValue: string;
	titleValue: string;
};

type Props = {
	onTypeChange: (newFilter: ThesisTypeFilter) => void;
	initialTypeValue: ThesisTypeFilter;

	onAdvisorChange: (advisorSubstr: string) => void;
	initialAdvisorValue: string;

	onTitleChange: (titleSubstr: string) => void;
	initialTitleValue: string;

	enabled: boolean;
};

const textFieldStyle = {
	marginLeft: "5px",
};

const labelStyle: React.CSSProperties = {
	fontWeight: "bold",
	fontSize: "110%",
};

const VALUE_CHANGE_TIMEOUT = 500;

export class TopFilters extends React.Component<Props, State> {
	private titleChangeTimeout: number | null = null;
	private advisorChangeTimeout: number | null = null;

	constructor(props: Props) {
		super(props);
		this.state = {
			advisorValue: props.initialAdvisorValue,
			titleValue: props.initialTitleValue,
			typeValue: props.initialTypeValue,
		};
	}

	private handleTypeChange = (newFilter: ThesisTypeFilter): void => {
		this.setState({
			typeValue: newFilter,
		});
		this.props.onTypeChange(newFilter);
	}

	private handleTitleChanged = (e: React.ChangeEvent<HTMLInputElement>): void => {
		if (this.titleChangeTimeout !== null) {
			window.clearTimeout(this.titleChangeTimeout);
		}
		this.setState({
			titleValue: e.target.value,
		});
		this.titleChangeTimeout = window.setTimeout(() => {
			this.titleChangeTimeout = null;
			this.props.onTitleChange(this.state.titleValue);
		}, VALUE_CHANGE_TIMEOUT);
	}

	private handleAdvisorChanged = (e: React.ChangeEvent<HTMLInputElement>): void => {
		if (this.advisorChangeTimeout !== null) {
			window.clearTimeout(this.advisorChangeTimeout);
		}
		this.setState({
			advisorValue: e.target.value,
		});
		this.advisorChangeTimeout = window.setTimeout(() => {
			this.advisorChangeTimeout = null;
			this.props.onAdvisorChange(this.state.advisorValue);
		}, VALUE_CHANGE_TIMEOUT);
	}

	public render() {
		return <div style={{
			width: "100%",
			display: "flex",
			justifyContent: "space-between",
			alignItems: "center",
		}}>
			<GenericSelect<ThesisTypeFilter>
				value={this.state.typeValue}
				onChange={this.handleTypeChange}
				optionInfo={typefilterInfos}
				label={"Rodzaj"}
				labelCss={labelStyle}
				enabled={this.props.enabled}
			/>

			<div>
				<span style={labelStyle}>Tytuł</span>
				<input
					type="text"
					value={this.state.titleValue}
					onChange={this.handleTitleChanged}
					style={textFieldStyle}
					disabled={!this.props.enabled}
				/>
			</div>

			<div>
				<span style={labelStyle}>Promotor</span>
				<input
					type="text"
					value={this.state.advisorValue}
					onChange={this.handleAdvisorChanged}
					style={textFieldStyle}
					disabled={!this.props.enabled}
				/>
			</div>
		</div>;
	}
}
