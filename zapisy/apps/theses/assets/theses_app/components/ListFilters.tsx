/**
 * Defines the filters component rendered above the theses table.
 */

import * as React from "react";
import styled from "styled-components";

import { GenericSelect } from "./GenericSelect";
import { ApplicationState } from "../app_types";
import { ThesisTypeFilter, thesisTypeFilterToString } from "../protocol_types";
import { StringFilter } from "../app_logic/theses_list";

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

	onOnlyMineChange: (onlyMine: boolean) => void;
	onlyMine: boolean;

	onAdvisorChange: (advisorSubstr: string) => void;
	advisorValue: string;

	onTitleChange: (titleSubstr: string) => void;
	titleValue: string;

	state: ApplicationState;
	stringFilterBeingChanged: StringFilter;
};

const TextFilterField = styled.input`
	margin-left: 5px;
	width: 150px;
`;

const labelStyle: React.CSSProperties = {
	fontWeight: "bold",
	fontSize: "110%",
};

const OnlyMineContainer = styled.label`
	display: block;
	height: 28px;
	display: flex;
	align-items: center;
	color: inherit;
`;

const OnlyMineCheckbox = styled.input`
	/* _sigh_ bootstrap */
	margin-right: 5px !important;
`;

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

	private handleOnlyMineChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
		this.props.onOnlyMineChange(e.target.checked);
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
				<TextFilterField
					type="text"
					value={this.props.titleValue}
					onChange={this.handleTitleChanged}
					disabled={!(isNormalState || stringFilterBeingChanged === "title")}
				/>
			</div>

			<div>
				<span style={labelStyle}>Promotor</span>
				<TextFilterField
					type="text"
					value={this.props.advisorValue}
					onChange={this.handleAdvisorChanged}
					disabled={!(isNormalState || stringFilterBeingChanged === "advisor")}
				/>
			</div>

			<OnlyMineContainer>
				<OnlyMineCheckbox
					type="checkbox"
					checked={this.props.onlyMine}
					onChange={this.handleOnlyMineChange}
					disabled={!isNormalState}
				/>
				<span style={labelStyle}>Tylko moje</span>
			</OnlyMineContainer>
		</FiltersContainer>;
	}
}
