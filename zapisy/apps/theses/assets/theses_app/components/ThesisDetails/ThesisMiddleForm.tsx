import * as React from "react";
import "react-select/dist/react-select.css";
import AsyncPaginate from "./ReactSelectAsyncPaginate.jsx";

import styled from "styled-components";
import { Thesis } from "../../types";
import { getPersonAutocomplete, PersonType } from "../../backend_callers";

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

const SelectComponentWrapper = styled.div`
width: 50%;
`;

type SelectValueDef = {
	value: number;
	label: string;
};

class AsyncSelectAutocompleteGetter {
	private personType: PersonType;

	public constructor(personType: PersonType) {
		this.personType = personType;
	}

	public get = async (inputValue: string, _: any, lastPage: number) => {
		const thisPageNum = lastPage + 1;
		const acResults = await getPersonAutocomplete(this.personType, inputValue, thisPageNum);
		const result = acResults.results.map(pac => ({ value: pac.id, label: pac.text }));
		return {
			options: result,
			hasMore: acResults.pagination.more,
			page: thisPageNum,
		};
	}
}

type Props = {
	thesis: Thesis;
};

type State = {
	currentAdvisorId: number | null;
	currentStudentId: number | null;
};

export class ThesisMiddleForm extends React.Component<Props, State> {
	public constructor(props: Props) {
		super(props);
		this.state = {
			currentAdvisorId: this.props.thesis.advisor.id,
			currentStudentId: this.props.thesis.student.id,
		};
	}

	public render() {
		return <div>
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
					<td></td>
				</tr>
				<tr>
					<td>Student</td>
					<td><SelectComponentWrapper><AsyncPaginate
						cacheOptions
						defaultOptions
						loadOptions={(new AsyncSelectAutocompleteGetter(PersonType.Student)).get}
						onChange={this.onStudentChanged}
						// value={this.state.currentStudentId}
						baseOptions={[this.getBaseStudentOptions()]}
					/></SelectComponentWrapper></td>
				</tr>
				</tbody>
			</MidFormTable>
			<textarea
				style={{ width: "100%", height: "100px", boxSizing: "border-box" }}
				defaultValue={this.props.thesis.description}
			/>
		</div>;
	}

	private getBaseStudentOptions(): SelectValueDef {
		return {
			value: this.props.thesis.student.id,
			label: this.props.thesis.student.getDisplayName(),
		};
	}

	private onStudentChanged = (newValue: SelectValueDef | null): void => {
		this.setState({
			currentStudentId: newValue ? Number(newValue.value) : null,
		});
	}
}
