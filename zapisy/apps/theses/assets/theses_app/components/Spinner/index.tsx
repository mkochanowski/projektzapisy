/**
 * @file A simple spinner component used as a base by other components
 */

import * as React from "react";
import spinner from "./spinner_transparent.gif";

type Props = {
	style?: React.CSSProperties;
};
export const Spinner = React.memo(function(props: Props): JSX.Element {
	return <img
		src={spinner}
		style={Object.assign({
			zIndex: 999,
			width: "300px",
		}, props.style)}
	/>;
});
