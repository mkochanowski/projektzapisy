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

	enabled: boolean;
};

const textFieldStyle = {
	marginLeft: "5px",
};

const labelStyle: React.CSSProperties = {
	fontWeight: "bold",
	fontSize: "110%",
};

export class ListFilters extends React.PureComponent<Props> {
	private handleTypeChange = (newFilter: ThesisTypeFilter): void => {
		this.props.onTypeChange(newFilter);
	}

	private handleTitleChanged = (e: React.ChangeEvent<HTMLInputElement>): void => {
		this.props.onTitleChange(e.target.value);
	}

	private handleAdvisorChanged = (e: React.ChangeEvent<HTMLInputElement>): void => {
		this.props.onAdvisorChange(e.target.value);
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
					value={this.props.titleValue}
					onChange={this.handleTitleChanged}
					style={textFieldStyle}
					disabled={!this.props.enabled}
				/>
			</div>

			<div>
				<span style={labelStyle}>Promotor</span>
				<input
					type="text"
					value={this.props.advisorValue}
					onChange={this.handleAdvisorChanged}
					style={textFieldStyle}
					disabled={!this.props.enabled}
				/>
			</div>
		</div>;
	}
}
