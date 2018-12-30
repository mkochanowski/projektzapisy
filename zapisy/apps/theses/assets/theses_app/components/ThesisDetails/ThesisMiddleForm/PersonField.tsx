/**
 * @file Implements a <select> based person field with async loading
 * and text search, used for students and advisors
 */
import * as React from "react";
import "react-select/dist/react-select.css";
import styled from "styled-components";
import AsyncPaginate from "react-select-async-paginate";

import { getPersonAutocomplete, PersonType } from "../../../backend_callers";
import { BasePerson } from "../../../types";
import { ReadOnlyInput } from "./ReadOnlyInput";

const PersonFieldWrapper = styled.div`
	width: 50%;
	display: inline-block;
`;
const PersonIndicatorInput = styled(ReadOnlyInput)`
	height: 36px;
	width: 100%;
	box-sizing: border-box;
`;

// This uses django-autocomplete-light's endpoint to fetch a list of
// matching employees/students, which dictates the person format defined below
// For an explanation of django-autocomplete-light, look in forms.py

type Props = {
	value: BasePerson | null;
	onChange: (newValue: BasePerson | null) => void;
	/** Student or Employee */
	personType: PersonType;
	readOnly?: boolean;
};

export class PersonField extends React.PureComponent<Props> {
	/** Used so that we know which page to ask for in getResults */
	private pageNumberForInput: Map<string, number> = new Map();

	public render() {
		const { props } = this;
		const isReadOnly = typeof props.readOnly !== "undefined" ? props.readOnly : false;
		const valueComponent = isReadOnly
			? <PersonIndicatorInput
				text={props.value ? props.value.displayName : "<brak>"}
			/>
			: <AsyncPaginate
				cacheOptions
				defaultOptions
				loadOptions={this.getResults}
				onChange={(nv: PersonSelectOptions | null) => props.onChange(selectOptionsToPerson(nv))}
				value={personToSelectOptions(props.value)}
				placeholder={"Wybierz..."}
				noResultsText={""}
			/>;

		return <PersonFieldWrapper>{valueComponent}</PersonFieldWrapper>;
	}

	private getResults = async (inputValue: string, _: any) => {
		const thisPageNum = this.pageNumberForInput.get(inputValue) || 1;
		try {
			const acResults = await getPersonAutocomplete(this.props.personType, inputValue, thisPageNum);
			const result = acResults.results.map(pac => ({ value: pac.id, label: pac.displayName }));
			this.pageNumberForInput.set(inputValue, thisPageNum + 1);

			return {
				options: result,
				hasMore: acResults.hasMore,
				page: thisPageNum,
			};
		} catch (err) {
			alert(`Nie udało się pobrać listy (${err.toString()}); odśwież stronę lub spróbuj później`);
		}
	}
}

type PersonSelectOptions = {
	value: string;
	label: string;
};

function personToSelectOptions(person: BasePerson | null): PersonSelectOptions | null {
	return person ? {
		value: String(person.id),
		label: person.displayName,
	} : null;
}

function selectOptionsToPerson(options: PersonSelectOptions | null): BasePerson | null {
	return options ? new BasePerson(
		Number(options.value),
		options.label,
	) : null;
}
