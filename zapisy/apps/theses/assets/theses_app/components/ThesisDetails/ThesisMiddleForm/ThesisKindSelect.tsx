import * as React from "react";

import { ThesisKind, thesisKindToString } from "../../../types";
import { GenericSelect } from "../../GenericSelect";

const kindSelectInfos = [
	ThesisKind.Masters,
	ThesisKind.Engineers,
	ThesisKind.Bachelors,
	ThesisKind.BachelorsEngineers,
	ThesisKind.Isim,
].map(kind => ({ val: kind, displayName: thesisKindToString(kind) }));

export type ThesisKindSelectProps = {
	value: ThesisKind;
	onChange: (k: ThesisKind) => void;
};
export function ThesisKindSelect(props: ThesisKindSelectProps) {
	return <GenericSelect<ThesisKind>
		{...props}
		optionInfo={kindSelectInfos}
	/>;
}
