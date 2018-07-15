import * as React from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import * as moment from "moment";

import { Thesis } from "../../types";

type Props = {
	thesis: Thesis;
};

export class ThesisTopRow extends React.Component<Props> {
	public render() {
		return <div style={{
			display: "flex",
			flexDirection: "row",
			gridColumnGap: "10px",
			columnGap: "10px",
			justifyContent: "space-between",
			width: "100%"
		}}>
			<span><input
				type="checkbox"
				checked={this.props.thesis.reserved}
				readOnly
				style={{ position: "relative", verticalAlign: "middle" }}
			/> {this.props.thesis.reserved ? "zarezerwowana" : "wolna"}</span>
			<table>
				<tbody>
				<tr>
					<td style={{ paddingRight: "5px" }}>
						<span>Aktualizacja</span>
					</td>
					<td>
					<DatePicker
						selected={moment(this.props.thesis.modifiedDate)}
						onChange={this.dateChanged}
						todayButton="Today"
					/>
					</td>
				</tr>
				</tbody>
			</table>
			<span>Status {this.props.thesis.status}</span>
		</div>;
	}

	private dateChanged = (newDate: moment.Moment) => {
		console.warn("new date", newDate.toDate());
	}
}
