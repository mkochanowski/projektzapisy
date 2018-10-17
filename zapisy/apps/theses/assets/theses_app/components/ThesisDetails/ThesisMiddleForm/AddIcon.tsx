import * as React from "react";

import AddIconImage from "./add-icon.png";

type Props = {
	onClick: () => void;
};

export function AddIcon(props: Props) {
	return <img
		src={AddIconImage}
		onClick={props.onClick}
	/>;
}
