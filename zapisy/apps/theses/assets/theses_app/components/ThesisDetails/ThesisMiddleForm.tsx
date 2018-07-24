import * as React from "react";
import "react-select/dist/react-select.css";
import AsyncPaginate from "react-select-async-paginate";

import styled from "styled-components";
import { Thesis, BasePerson } from "../../types";
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
	value: string;
	label: string;
};

class AsyncSelectAutocompleteGetter {
	private personType: PersonType;

	public constructor(personType: PersonType) {
		this.personType = personType;
	}

	public get = async (inputValue: string, _: any, lastPage: number = 0) => {
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
	currentAuxAdvisorId: number | null;
	currentStudentValue: SelectValueDef | null;
	currentSecondStudentId: number | null;
};

export class ThesisMiddleForm extends React.Component<Props, State> {
	public constructor(props: Props) {
		super(props);
		const thesis = this.props.thesis;
		this.state = {
			currentAdvisorId: thesis.advisor ? thesis.advisor.id : null,
			currentAuxAdvisorId: thesis.auxiliaryAdvisor ? thesis.auxiliaryAdvisor.id : null,
			currentStudentValue: thesis.student ? this.getBaseOptionsForPerson(thesis.student) : null,
			currentSecondStudentId: thesis.secondStudent ? thesis.secondStudent.id : null,
		};
	}

	public render() {
		const thesis = this.props.thesis;
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
						value={this.state.currentStudentValue}
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

	private getBaseOptionsForPerson(person: BasePerson | undefined): SelectValueDef | null {
		return person ? {
			value: String(person.id),
			label: person.getDisplayName(),
		} : null;
	}

	private makeOnPersonChangedHandler(fieldName: keyof State) {
		return (newValue: SelectValueDef | null): void => {
			this.setState({
				[fieldName]: newValue || null,
			} as any);
		};
	}

	private onStudentChanged = this.makeOnPersonChangedHandler("currentStudentValue");
	private onAdvisorChanged = this.makeOnPersonChangedHandler("currentAdvisorId");
}
