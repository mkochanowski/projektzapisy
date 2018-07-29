import * as React from "react";

type SelectOptionsInfo<T> = Array<{
	val: T;
	displayName: string;
}>;

type Props<T> = {
	value: T;
	onChange: (val: T) => void
	optionInfo: SelectOptionsInfo<T>;
	label?: string;
	labelCss?: React.CSSProperties;
};

export class GenericSelect<T> extends React.Component<Props<T>> {
	public render() {
		return <div>
				<span style={this.props.labelCss || {}}>{this.props.label || ""}</span>
				<select
					onChange={ev => this.onChange(ev.target.value)}
					value={String(this.getCurrentSelectValue())}
					style={this.props.label ? { marginLeft: "5px" } : {}}
				>
				{
					this.props.optionInfo.map((info, i) => (
						<option
							key={`status_filteropt_${i}`}
							value={String(info.val)}
						>
							{info.displayName}
						</option>
					))
				}
				</select>
		</div>;
	}

	private getCurrentSelectValue() {
		return this.props.optionInfo.find(info => info.val === this.props.value)!.val;
	}

	private onChange = (newValue: string) => {
		const convertedValue = this.stringValueToThesisStatus(newValue);
		if (convertedValue !== null) {
			this.props.onChange(convertedValue);
		}
	}

	private stringValueToThesisStatus(stringValue: string): T | null {
		for (const info of this.props.optionInfo) {
			if (stringValue === String(info.val)) {
				return info.val;
			}
		}
		return null;
	}
}
