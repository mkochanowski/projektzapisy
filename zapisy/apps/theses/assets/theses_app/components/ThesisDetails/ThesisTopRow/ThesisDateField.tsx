import * as React from "react";
import * as moment from "moment";

type Props = {
	label: string;
	value: moment.Moment,
};

const FORMAT_STR = "DD/MM/YYYY HH:mm:ss";

export function ThesisDateField(props: Props) {
	return <table>
		<tbody>
			<tr>
				<td style={{ paddingRight: "5px" }}>
					<span>{props.label}</span>
				</td>
				<td>
				<input
					type={"text"}
					readOnly
					value={props.value.format(FORMAT_STR)}
				/>
				</td>
			</tr>
		</tbody>
	</table>;
}
