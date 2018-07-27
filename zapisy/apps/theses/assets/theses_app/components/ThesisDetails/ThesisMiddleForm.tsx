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
	border-top: 6px solid transparent;
}
td:first-child {
	border-left: 0;
}
tr:first-child td {
	border-top: 0;
}

tr td:first-child {
	width: 13%;
}
`;

const SelectComponentWrapper = styled.div`
width: 50%;
`;

const OptionalFieldLabel = styled.span`
font-style: italic;
`;

type SelectValueDef = {
	value: string;
	label: string;
};

class AsyncSelectAutocompleteGetter {
	private personType: PersonType;
	private pageNumberForInput: Map<string, number> = new Map();

	public constructor(personType: PersonType) {
		this.personType = personType;
	}

	public get = async (inputValue: string, _: any) => {
		const thisPageNum = this.pageNumberForInput.get(inputValue) || 1;

		const acResults = await getPersonAutocomplete(this.personType, inputValue, thisPageNum);
		const result = acResults.results.map(pac => ({ value: pac.id, label: pac.displayName }));

		this.pageNumberForInput.set(inputValue, thisPageNum + 1);

		return {
			options: result,
			hasMore: acResults.hasMore,
			page: thisPageNum,
		};
	}
}

type PersonSelectComponentProps = {
	value: SelectValueDef | null;
	onChange: (newValue: SelectValueDef | null) => void;
	personType: PersonType;
};
function PersonSelect(props: PersonSelectComponentProps) {
	return <SelectComponentWrapper><AsyncPaginate
		cacheOptions
		defaultOptions
		loadOptions={(new AsyncSelectAutocompleteGetter(props.personType)).get}
		onChange={props.onChange}
		value={props.value}
	/></SelectComponentWrapper>;
}

type Props = {
	thesis: Thesis;
};

type State = {
	advisorValue: SelectValueDef | null;
	auxAdvisorValue: SelectValueDef | null;
	studentValue: SelectValueDef | null;
	secondStudentValue: SelectValueDef | null;
};

export class ThesisMiddleForm extends React.Component<Props, State> {
	public constructor(props: Props) {
		super(props);
		const thesis = this.props.thesis;
		this.state = {
			advisorValue: this.getBaseOptionsForPerson(thesis.advisor),
			auxAdvisorValue: this.getBaseOptionsForPerson(thesis.auxiliaryAdvisor),
			studentValue: this.getBaseOptionsForPerson(thesis.student),
			secondStudentValue: this.getBaseOptionsForPerson(thesis.secondStudent),
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
					<td>
						<PersonSelect
							personType={PersonType.Employee}
							onChange={this.onAdvisorChanged}
							value={this.state.advisorValue}
						/>
					</td>
				</tr>
				<tr>
					<td><OptionalFieldLabel>Promotor wspomagający</OptionalFieldLabel></td>
					<td>
						<PersonSelect
							personType={PersonType.Employee}
							onChange={this.onAuxAdvisorChanged}
							value={this.state.auxAdvisorValue}
						/>
					</td>
				</tr>
				<tr>
					<td>Student</td>
					<td>
						<PersonSelect
							personType={PersonType.Student}
							onChange={this.onStudentChanged}
							value={this.state.studentValue}
						/>
					</td>
				</tr>
				<tr>
					<td><OptionalFieldLabel>Student wspomagający</OptionalFieldLabel></td>
					<td>
						<PersonSelect
							personType={PersonType.Student}
							onChange={this.onSecondStudentChanged}
							value={this.state.secondStudentValue}
						/>
					</td>
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
			label: person.displayName,
		} : null;
	}

	private makeOnPersonChangedHandler(fieldName: keyof State) {
		return (newValue: SelectValueDef | null): void => {
			this.setState({
				[fieldName]: newValue || null,
			// TS doesn't allow anything other than a generic [string] key type
			// (so we can't have a union of strings as a key type)
			// hence this cast
			} as any);
		};
	}

	private onStudentChanged = this.makeOnPersonChangedHandler("studentValue");
	private onSecondStudentChanged = this.makeOnPersonChangedHandler("secondStudentValue");
	private onAdvisorChanged = this.makeOnPersonChangedHandler("advisorValue");
	private onAuxAdvisorChanged = this.makeOnPersonChangedHandler("auxAdvisorValue");
}
