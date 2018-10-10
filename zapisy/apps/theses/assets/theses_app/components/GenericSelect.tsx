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
	enabled?: boolean;
};

export class GenericSelect<T> extends React.Component<Props<T>> {
	public render() {
		const shouldDisable = typeof this.props.enabled === "boolean" ? !this.props.enabled : false;
		const styles: React.CSSProperties = {};
		if (shouldDisable) {
			Object.assign(styles, { backgroundColor: "lightgray" });
		}
		if (this.props.label) {
			Object.assign(styles, { marginLeft: "5px" });
		}
		return <div>
				<span style={this.props.labelCss || {}}>{this.props.label || ""}</span>
				<select
					onChange={ev => this.onChange(ev.target.value)}
					value={String(this.getCurrentSelectValue())}
					style={styles}
					disabled={shouldDisable}
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
