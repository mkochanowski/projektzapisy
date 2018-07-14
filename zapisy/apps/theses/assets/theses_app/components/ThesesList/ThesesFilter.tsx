import * as React from "react";
import { ThesisTypeFilter } from "../../backend_callers";

type Props = {
	onChanged: (newFilter: ThesisTypeFilter) => void;
	initialValue: ThesisTypeFilter;
};

type ThesisTypeFilterInfo = {
	val: ThesisTypeFilter;
	stringVal: string;
	displayName: string;
};
const filterInfos: ThesisTypeFilterInfo[] = [
	{ val: ThesisTypeFilter.AllCurrent, stringVal: "all_current", displayName: "Wszystkie aktualne" },
	{ val: ThesisTypeFilter.All, stringVal: "all", displayName: "Wszystkie" },
	{ val: ThesisTypeFilter.Masters, stringVal: "masters", displayName: "Magisterskie" },
	{ val: ThesisTypeFilter.Engineers, stringVal: "engineers", displayName: "Inżynierskie" },
	{ val: ThesisTypeFilter.Bachelors, stringVal: "bachelors", displayName: "Licencjackie" },
	{ val: ThesisTypeFilter.BachelorsISIM, stringVal: "bachelors_isim", displayName: "Licencjackie ISIM" },
	{ val: ThesisTypeFilter.AvailableMasters, stringVal: "available_masters", displayName: "Magisterskie - dostępne" },
	{ val: ThesisTypeFilter.AvailableEngineers, stringVal: "available_engineers", displayName: "Inżynierskie - dostępne" },
	{ val: ThesisTypeFilter.AvailableBachelors, stringVal: "available_bachelors", displayName: "Licencjackie - dostępne" },
	{ val: ThesisTypeFilter.AvailableBachelorsISIM, stringVal: "available_bachelors_isim", displayName: "Licencjackie ISIM - dostępne" },
];

export class ThesesFilter extends React.Component<Props> {
	render() {
		return <div style={{
			textAlign: "right",
			width: "100%",
		}}>
			<strong>Rodzaj </strong>
			<select
				onChange={ev => this.onChanged(ev.target.value)}
				defaultValue={this.findDefaultStringValue()}
			>
				{
					filterInfos.map((info, i) => (
						<option
							key={`filteropt_${i}`}
							value={info.stringVal}
						>
							{info.displayName}
						</option>
					))
				}
			</select>
		</div>;
	}

	private findDefaultStringValue(): string {
		return filterInfos.find(info => info.val === this.props.initialValue)!.stringVal;
	}

	private onChanged = (newValue: string) => {
		const convertedValue = stringValueToThesisFilter(newValue);
		if (convertedValue !== null) {
			this.props.onChanged(convertedValue);
		}
	}
}

function stringValueToThesisFilter(stringValue: string): ThesisTypeFilter | null {
	for (const info of filterInfos) {
		if (stringValue === info.stringVal) {
			return info.val;
		}
	}
	return null;
}
