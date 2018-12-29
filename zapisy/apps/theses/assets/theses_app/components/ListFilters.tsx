/**
 * Defines the filters component rendered above the theses table.
 */

import * as React from "react";
import styled from "styled-components";

import { GenericSelect } from "./GenericSelect";
import { ThesisTypeFilter, thesisTypeFilterToString } from "../types";
import { ApplicationState } from "../types/misc";
import { ChangedStringFilter } from "../theses_store";

const typeFilterInfos = [
	ThesisTypeFilter.AllCurrent,
	ThesisTypeFilter.All,
	ThesisTypeFilter.Masters,
	ThesisTypeFilter.Engineers,
	ThesisTypeFilter.Bachelors,
	ThesisTypeFilter.BachelorsISIM,
	ThesisTypeFilter.AvailableMasters,
	ThesisTypeFilter.AvailableEngineers,
	ThesisTypeFilter.AvailableBachelors,
	ThesisTypeFilter.AvailableBachelorsISIM,
].map(type => ({ val: type, displayName: thesisTypeFilterToString(type) }));

type Props = {
	onTypeChange: (newFilter: ThesisTypeFilter) => void;
	typeValue: ThesisTypeFilter;

	onAdvisorChange: (advisorSubstr: string) => void;
	advisorValue: string;

	onTitleChange: (titleSubstr: string) => void;
	titleValue: string;

	state: ApplicationState;
	stringFilterBeingChanged: ChangedStringFilter;
};

const textFieldStyle = {
	marginLeft: "5px",
};

const labelStyle: React.CSSProperties = {
	fontWeight: "bold",
	fontSize: "110%",
};

const FiltersContainer = styled.div`
	width: 100%;
	display: flex;
	justify-content: space-between;
	align-items: center;
`;

export class ListFilters extends React.PureComponent<Props> {
	private handleTypeChange = (newFilter: ThesisTypeFilter): void => {
		this.props.onTypeChange(newFilter);
	}

	private handleTitleChanged = (e: React.ChangeEvent<HTMLInputElement>): void => {
		this.props.onTitleChange(e.target.value);
	}

	private handleAdvisorChanged = (e: React.ChangeEvent<HTMLInputElement>): void => {
		this.props.onAdvisorChange(e.target.value);
	}

	public render() {
		const { state, stringFilterBeingChanged } = this.props;
		if (stringFilterBeingChanged !== "") {
			console.assert(
				state === ApplicationState.Refetching,
				"While changing string filters we should fetching",
			);
		}
		const isNormalState = state === ApplicationState.Normal;
		return <FiltersContainer>
			<GenericSelect<ThesisTypeFilter>
				value={this.props.typeValue}
				onChange={this.handleTypeChange}
				optionInfo={typeFilterInfos}
				label={"Rodzaj"}
				labelCss={labelStyle}
				enabled={isNormalState}
			/>

			<div>
				<span style={labelStyle}>Tytuł</span>
				<input
					type="text"
					value={this.props.titleValue}
					onChange={this.handleTitleChanged}
					style={textFieldStyle}
					disabled={!(isNormalState || stringFilterBeingChanged === "title")}
				/>
			</div>

			<div>
				<span style={labelStyle}>Promotor</span>
				<input
					type="text"
					value={this.props.advisorValue}
					onChange={this.handleAdvisorChanged}
					style={textFieldStyle}
					disabled={!(isNormalState || stringFilterBeingChanged === "advisor")}
				/>
			</div>
		</FiltersContainer>;
	}
}
