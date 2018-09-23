import * as React from "react";
import * as moment from "moment";

type Props = {
	value: moment.Moment,
};

const FORMAT_STR = "DD/MM/YYYY HH:mm:ss";

export class DateUpdatedField extends React.Component<Props> {
	public render() {
		return <table>
			<tbody>
				<tr>
					<td style={{ paddingRight: "5px" }}>
						<span>Aktualizacja</span>
					</td>
					<td>
					<input
						type={"text"}
						readOnly
						value={this.props.value.format(FORMAT_STR)}
					/>
					</td>
				</tr>
			</tbody>
		</table>;
	}
}
