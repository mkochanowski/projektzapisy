import * as React from "react";

import { ThesisStatus } from "../../../types";

type ThesisStatusFilterInfo = {
	val: ThesisStatus;
	displayName: string;
};
const filterInfos: ThesisStatusFilterInfo[] = [
	{ val: ThesisStatus.Accepted, displayName: "Zaakceptowana" },
	{ val: ThesisStatus.BeingEvaluated, displayName: "Poddana pod głosowanie" },
	{ val: ThesisStatus.Defended, displayName: "Obroniona" },
	{ val: ThesisStatus.InProgress, displayName: "W realizacji" },
	{
		val: ThesisStatus.ReturnedForCorrections, displayName: "Zwrócona do poprawek"
	},

];

type Props = {
	value: ThesisStatus,
	onChange: (val: ThesisStatus) => void
};

export class ThesisStatusIndicator extends React.Component<Props> {
	public render() {
		return <div>
			<span>Status </span>
			<select
				onChange={ev => this.onChange(ev.target.value)}
				value={this.getCurrentSelectValue()}
			>
				{
					filterInfos.map((info, i) => (
						<option
							key={`status_filteropt_${i}`}
							value={info.val}
						>
							{info.displayName}
						</option>
					))
				}
			</select>
		</div>;
	}

	private getCurrentSelectValue() {
		return filterInfos.find(info => info.val === this.props.value)!.val;
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
		if (Number(stringValue) === info.val) {
			return info.val;
		}
	}
	return null;
}
