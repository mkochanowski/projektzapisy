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

type Props = {
	onTypeChange: (newFilter: ThesisTypeFilter) => void;
	typeValue: ThesisTypeFilter;

	onAdvisorChange: (advisorSubstr: string) => void;
	advisorValue: string;

	onTitleChange: (titleSubstr: string) => void;
	titleValue: string;
};

const textFieldStyle = {
	marginLeft: "5px",
};

const labelStyle: React.CSSProperties = {
	fontWeight: "bold",
	fontSize: "110%",
};

const VALUE_CHANGE_TIMEOUT = 500;

export class TopFilters extends React.Component<Props> {
	private titleChangeTimeout: number | null = null;
	private advisorChangeTimeout: number | null = null;

	private handleTitleChanged = (e: React.ChangeEvent<HTMLInputElement>): void => {
		if (this.titleChangeTimeout !== null) {
			window.clearTimeout(this.titleChangeTimeout);
		}
		this.titleChangeTimeout = window.setTimeout(() => {
			this.titleChangeTimeout = null;
			this.props.onTitleChange(e.target.value);
		}, VALUE_CHANGE_TIMEOUT);
	}

	private handleAdvisorChanged = (e: React.ChangeEvent<HTMLInputElement>): void => {
		if (this.advisorChangeTimeout !== null) {
			window.clearTimeout(this.advisorChangeTimeout);
		}
		this.advisorChangeTimeout = window.setTimeout(() => {
			this.advisorChangeTimeout = null;
			this.props.onAdvisorChange(e.target.value);
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
				value={this.props.typeValue}
				onChange={this.props.onTypeChange}
				optionInfo={typefilterInfos}
				label={"Rodzaj"}
				labelCss={labelStyle}
			/>

			<div>
				<span style={labelStyle}>Tytuł</span>
				<input
					type="text"
					value={this.props.titleValue}
					onChange={this.handleTitleChanged}
					style={textFieldStyle}
				/>
			</div>

			<div>
				<span style={labelStyle}>Promotor</span>
				<input
					type="text"
					value={this.props.advisorValue}
					onChange={this.handleAdvisorChanged}
					style={textFieldStyle}
				/>
			</div>
		</div>;
	}
}
