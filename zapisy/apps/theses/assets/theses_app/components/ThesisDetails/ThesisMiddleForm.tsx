import * as React from "react";
import styled from "styled-components";
import { Thesis } from "../../types";

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
	thesis: Thesis;
};

export function ThesisMiddleForm(props: Props): JSX.Element {
	return <div>
			<MidFormTable>
				<tbody>
				<tr>
					<td>Tytuł</td>
					<td><textarea
						style={{ width: "100%", boxSizing: "border-box" }}
						defaultValue={props.thesis.title}
					/></td>
				</tr>
				<tr>
					<td>Promotor</td>
					<td><BorderBoxedInput
						type="text"
						style={{ width: "50%" }}
						defaultValue={props.thesis.advisor.getDisplayName()}
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
			defaultValue={props.thesis.description}
		/>
	</div>;
}
