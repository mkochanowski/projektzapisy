import * as React from "react";
import * as ReactDOM from "react-dom";

import { whenDomLoaded } from "common/utils";
import { ThesesApp } from "./components/ThesesApp";

function main() {
	console.warn("Theses system: React main");
	ReactDOM.render(
		<ThesesApp />,
		document.getElementById("theses-react-root"),
	);
}
whenDomLoaded(main);
