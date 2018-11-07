import * as React from "react";
import styled from "styled-components";

import AddIconImage from "./add-icon.png";
import RemoveIconImage from "./remove-icon.png";

export const enum IconType {
	Add,
	Remove,
}

type Props = {
	type: IconType,
	onClick: () => void;
};

const IconImg = styled.img`
	vertical-align: top;
	margin-top: 7.5px;
	margin-left: 10px;
	width: 16px;
	cursor: pointer;
`;

export function AddRemoveIcon(props: Props) {
	return <IconImg
		src={props.type === IconType.Add ? AddIconImage : RemoveIconImage}
		onClick={props.onClick}
	/>;
}
