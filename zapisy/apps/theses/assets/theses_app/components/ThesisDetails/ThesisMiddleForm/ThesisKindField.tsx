/**
 * @file Displays (and optionally allows to modify)the kind of a thesis
 */

import * as React from "react";

import { ThesisKind, thesisKindToString } from "../../../types";
import { GenericSelect } from "../../GenericSelect";
import { ReadOnlyInput } from "./ReadOnlyInput";

const kindSelectInfos = [
	ThesisKind.Masters,
	ThesisKind.Engineers,
	ThesisKind.Bachelors,
	ThesisKind.BachelorsEngineers,
	ThesisKind.Isim,
].map(kind => ({ val: kind, displayName: thesisKindToString(kind) }));

export type ThesisKindSelectProps = {
	value: ThesisKind;
	readOnly: boolean;
	onChange: (k: ThesisKind) => void;
};
export function ThesisKindField(props: ThesisKindSelectProps) {
	return props.readOnly
	? <ReadOnlyInput
		text={thesisKindToString(props.value)}
		style={{ width: "210px" }}
	/>
	: <GenericSelect<ThesisKind>
		value={props.value}
		onChange={props.onChange}
		optionInfo={kindSelectInfos}
	/>;
}
