import * as React from "react";
import styled from "styled-components";

import { Thesis } from "../../types";
import { ThesisTopRow } from "./ThesisTopRow";

const MidFormTable = styled.table`
	width: 100%;

	td {
		border-left: 4px solid transparent;
		border-top: 4px solid transparent;
	}
	td:first-child {
		border-left: 0;
	}
	tr:first-child td {
		border-top: 0;
	}

	tr td:first-child {
		width: 10%;
	}
`;

const BorderBoxedInput = styled.input`
	box-sizing: border-box;
`;

type Props = {
	thesis: Thesis,
};

export class ThesisDetails extends React.Component<Props> {
	public render() {
		return <div style= {{
			border: "1px solid black",
			padding: "15px",
		}}>
			<ThesisTopRow
				thesis={this.props.thesis}
			/>
			<MidFormTable>
				<tbody>
				<tr>
					<td>Tytuł</td>
					<td><textarea
						style={{ width: "100%", boxSizing: "border-box" }}
						defaultValue={this.props.thesis.title}
					/></td>
				</tr>
				<tr>
					<td>Promotor</td>
					<td><BorderBoxedInput
						type="text"
						style={{ width: "50%" }}
						defaultValue={this.props.thesis.advisor.getDisplayName()}
					/></td>
				</tr>
				<tr>
					<td>Student</td>
					<td><BorderBoxedInput
						type="text"
						style={{ width: "50%" }}
						defaultValue={"Dupa 123"}
					/></td>
				</tr>
				</tbody>
			</MidFormTable>
			<textarea
				style={{ width: "100%", height: "100px", boxSizing: "border-box" }}
				defaultValue={"This is a very long description of what some poor sod must do"}
			/>
		</div>;
	}
}
