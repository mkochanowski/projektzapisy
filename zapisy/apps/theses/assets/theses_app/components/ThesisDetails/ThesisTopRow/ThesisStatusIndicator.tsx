import * as React from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import * as moment from "moment";

import { ThesisStatus } from "../../../types";

type ThesisStatusFilterInfo = {
	val: ThesisStatus;
	stringVal: string;
	displayName: string;
};
const filterInfos: ThesisStatusFilterInfo[] = [
	{ val: ThesisStatus.Accepted, stringVal: "accepted", displayName: "Zaakceptowana" },
	{ val: ThesisStatus.BeingEvaluated, stringVal: "evaluated", displayName: "Poddana pod głosowanie" },
	{ val: ThesisStatus.Defended, stringVal: "defended", displayName: "Obroniona" },
	{ val: ThesisStatus.InProgress, stringVal: "in_progress", displayName: "W realizacji" },
	{ val: ThesisStatus.ReturnedForCorrections, stringVal: "returned", displayName: "Zwrócona do poprawek" },

];

type Props = {
	initialValue: ThesisStatus,
	onChange: (val: ThesisStatus) => void
};

export class ThesisStatusIndicator extends React.Component<Props> {
	public render() {
		return <div>
			<span>Status </span>
			<select
				onChange={ev => this.onChange(ev.target.value)}
				defaultValue={this.findDefaultStringValue()}
			>
				{
					filterInfos.map((info, i) => (
						<option
							key={`status_filteropt_${i}`}
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

	private onChange = (newValue: string) => {
		const convertedValue = stringValueToThesisStatus(newValue);
		if (convertedValue !== null) {
			this.props.onChange(convertedValue);
		}
	}
}

function stringValueToThesisStatus(stringValue: string): ThesisStatus | null {
	for (const info of filterInfos) {
		if (stringValue === info.stringVal) {
			return info.val;
		}
	}
	return null;
}
