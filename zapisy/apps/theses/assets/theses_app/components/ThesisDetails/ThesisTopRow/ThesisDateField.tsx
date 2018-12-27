import * as React from "react";
import * as moment from "moment";
import { InputWithLabel, InputType } from "./InputWithLabel";

type Props = {
	label: string;
	value?: moment.Moment,
};

const FORMAT_STR = "DD/MM/YYYY HH:mm:ss";

export const ThesisDateField = React.memo(function(props: Props) {
	const { label, value } = props;
	return <InputWithLabel
		labelText={label}
		inputText={value ? value.format(FORMAT_STR) : ""}
		inputType={InputType.ReadOnly}
	/>;
});
