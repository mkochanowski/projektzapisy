import * as React from "react";

import { ThesisStatus, thesisStatusToString } from "../../../types";
import { GenericSelect } from "../../GenericSelect";
import { InputWithLabel, InputType } from "./InputWithLabel";

const LABEL_TEXT = "Status";

const statusSelectInfos = [
	ThesisStatus.BeingEvaluated,
	ThesisStatus.Accepted,
	ThesisStatus.InProgress,
	ThesisStatus.Defended,
	ThesisStatus.ReturnedForCorrections,
].map(kind => ({ val: kind, displayName: thesisStatusToString(kind) }));

type Props = {
	value: ThesisStatus;
	onChange: (val: ThesisStatus) => void;
	enabled: boolean;
};

/**
 * Shows the thesis status in a <select> field if modification
 * is allowed or a read-only text input otherwise
 */
export const ThesisStatusIndicator = React.memo(function(props: Props) {
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
});
