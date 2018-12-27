/**
 * @file The "add new thesis" button component shown above the theses table
 * 	if the user has the necessary permissions
 */

import * as React from "react";
import StandardButton from "react-button-component";
import styled from "styled-components";

const Button = styled(StandardButton)`
	width: 100px;
	min-height: initial;
	height: 30px;
	margin-left: 40px;
`;

type Props = {
	onClick: () => void;
};

export const AddNewButton = React.memo(function(props: Props) {
	return <Button onClick={props.onClick}>Dodaj nową</Button>;
});
