import * as React from "react";
import "react-select/dist/react-select.css";
import styled from "styled-components";
import AsyncPaginate from "react-select-async-paginate";

import { getPersonAutocomplete, PersonType } from "../../../backend_callers";

const SelectComponentWrapper = styled.div`
width: 50%;
`;

export type AsyncSelectValueDef = {
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
	value: AsyncSelectValueDef | null;
	onChange: (newValue: AsyncSelectValueDef | null) => void;
	personType: PersonType;
};

export function PersonSelect(props: PersonSelectComponentProps) {
	return <SelectComponentWrapper><AsyncPaginate
		cacheOptions
		defaultOptions
		loadOptions={(new AsyncSelectAutocompleteGetter(props.personType)).get}
		onChange={props.onChange}
		value={props.value}
	/></SelectComponentWrapper>;
}
