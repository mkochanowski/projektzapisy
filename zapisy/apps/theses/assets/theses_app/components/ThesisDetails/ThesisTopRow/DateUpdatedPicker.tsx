import * as React from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import * as moment from "moment";

type Props = {
	initialValue: Date,
	onChange: (val: Date) => void
};
type State = {
	currentDate: Date;
};

export class DateUpdatedPicker extends React.Component<Props, State> {
	public constructor(props: Props) {
		super(props);
		this.state = {
			currentDate: props.initialValue,
		};
	}

	public render() {
		return <table>
			<tbody>
				<tr>
					<td style={{ paddingRight: "5px" }}>
						<span>Aktualizacja</span>
					</td>
					<td>
					<DatePicker
						selected={moment(this.state.currentDate)}
						onChange={this.onChange}
						todayButton="Today"
					/>
					</td>
				</tr>
			</tbody>
		</table>;
	}

	private onChange = (newMoment: moment.Moment): void => {
		const newDate = newMoment.toDate();
		this.setState({ currentDate: newDate });
		this.props.onChange(newDate);
	}
}
