import * as React from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import * as moment from "moment";

type Props = {
	value: moment.Moment,
	onChange: (val: moment.Moment) => void
};

export class DateUpdatedPicker extends React.Component<Props> {
	public render() {
		return <table>
			<tbody>
				<tr>
					<td style={{ paddingRight: "5px" }}>
						<span>Aktualizacja</span>
					</td>
					<td>
					<DatePicker
						selected={moment(this.props.value)}
						onChange={this.props.onChange}
						todayButton="Today"
					/>
					</td>
				</tr>
			</tbody>
		</table>;
	}
}
