import { ThesisStatus } from "../../../types";
import { GenericSelect } from "../../GenericSelect";

const filterInfos = [
	{ val: ThesisStatus.Accepted, displayName: "Zaakceptowana" },
	{ val: ThesisStatus.BeingEvaluated, displayName: "Poddana pod głosowanie" },
	{ val: ThesisStatus.Defended, displayName: "Obroniona" },
	{ val: ThesisStatus.InProgress, displayName: "W realizacji" },
	{
		val: ThesisStatus.ReturnedForCorrections, displayName: "Zwrócona do poprawek"
	},
];

type Props = {
	value: ThesisStatus;
	onChange: (val: ThesisStatus) => void;
};

export function ThesisStatusIndicator(props: Props) {
	return new (GenericSelect<ThesisStatus>("Status", filterInfos))(props);
}
