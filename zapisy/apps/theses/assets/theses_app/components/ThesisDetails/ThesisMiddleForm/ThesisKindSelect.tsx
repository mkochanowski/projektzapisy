import { ThesisKind } from "../../../types";
import { GenericSelect } from "../../GenericSelect";

const kindSelectInfos = [
	{ val: ThesisKind.Masters, displayName: "Magisterska" },
	{ val: ThesisKind.Engineers, displayName: "Inżynierska" },
	{ val: ThesisKind.Bachelors, displayName: "Licencjacka" },
	{ val: ThesisKind.BachelorsEngineers, displayName: "Lic+Inż" },
	{ val: ThesisKind.Isim, displayName: "ISIM" },
];

export type ThesisKindSelectProps = {
	value: ThesisKind;
	onChange: (k: ThesisKind) => void;
};
export function ThesisKindSelect(props: ThesisKindSelectProps) {
	return new (GenericSelect<ThesisKind>(kindSelectInfos))(props);
}
