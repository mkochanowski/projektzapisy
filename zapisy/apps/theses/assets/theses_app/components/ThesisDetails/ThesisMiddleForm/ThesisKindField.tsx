/**
 * @file Displays (and optionally allows to modify)the kind of a thesis
 */

import * as React from "react";

import { GenericSelect } from "../../GenericSelect";
import { ReadOnlyInput } from "./ReadOnlyInput";
import { ThesisKind, thesisKindToString } from "../../../protocol_types";

const kindSelectInfos = [
	ThesisKind.Bachelors,
	ThesisKind.Isim,
	ThesisKind.Engineers,
	ThesisKind.BachelorsEngineers,
	ThesisKind.Masters,
].map(kind => ({ val: kind, displayName: thesisKindToString(kind) }));

export type ThesisKindSelectProps = {
	value: ThesisKind;
	readOnly: boolean;
	onChange: (k: ThesisKind) => void;
};
export const ThesisKindField = React.memo(function(props: ThesisKindSelectProps) {
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
});
