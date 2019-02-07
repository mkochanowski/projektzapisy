/** @file Provides base components for dialogs. Used by specialized implementations */

import styled from "styled-components";

import "./dialog_styles.less";

export const DialogContainer = styled.div`
	font-family: Arial, Helvetica, sans-serif;
	width: 400px;
	padding: 30px;
	text-align: left;
	background: #fff;
	border-radius: 10px;
	box-shadow: 0 20px 75px rgba(0, 0, 0, 0.13);
	color: #666;

	& > h2 {
		margin-top: -10px;
		margin-bottom: 15px;
	}
`;

export const BaseButton = styled.button`
	text-shadow: none;
	background-image: none;
`;

export const ConfirmButton = styled(BaseButton)`
	color: #fff;
	background-color: #337ab7;
	border-color: #2e6da4;
	font-size: 14px;
	min-width: 100px;
	&:hover {
		color: #fff;
		filter: brightness(1.1);
	}
`;

export const ButtonsContainer = styled.div`
	margin-top: 20px;
`;
