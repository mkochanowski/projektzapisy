import * as React from "react";

export const enum InputType {
	Normal,
	ReadOnly,
	Disabled,
}

type Props = {
	labelText: string;
	inputText: string;
	inputWidth?: number;
	inputType: InputType,
};

/**
 * A simple component to render a text input with a label to the left,
 * used by more specific components
 */
export const InputWithLabel = React.memo(function(props: Props) {
	return <table>
		<tbody>
			<tr>
				<td style={{ paddingRight: "5px" }}>
					<span>{props.labelText}</span>
				</td>
				<td>
				<input
					type={"text"}
					value={props.inputText}
					style={{ width: props.inputWidth != null ? props.inputWidth : "auto" }}
					readOnly={props.inputType === InputType.ReadOnly}
					disabled={props.inputType === InputType.Disabled}
				/>
				</td>
			</tr>
		</tbody>
	</table>;
});
