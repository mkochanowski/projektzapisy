import * as React from "react";

import { ThesisStatus, thesisStatusToString } from "../../../types";
import { GenericSelect } from "../../GenericSelect";
import { InputWithLabel, InputType } from "./InputWithLabel";

const LABEL_TEXT = "Status";

const statusSelectInfos = [
	ThesisStatus.Accepted,
	ThesisStatus.BeingEvaluated,
	ThesisStatus.Defended,
	ThesisStatus.InProgress,
	ThesisStatus.ReturnedForCorrections,
].map(kind => ({ val: kind, displayName: thesisStatusToString(kind) }));

type Props = {
	value: ThesisStatus;
	onChange: (val: ThesisStatus) => void;
	enabled: boolean;
};

export function ThesisStatusIndicator(props: Props) {
	return props.enabled
	? <GenericSelect<ThesisStatus>
		{...props}
		optionInfo={statusSelectInfos}
		label={LABEL_TEXT}
	/>
	: <InputWithLabel
		labelText={LABEL_TEXT}
		inputText={thesisStatusToString(props.value)}
		inputType={InputType.ReadOnly}
	/>;
}
