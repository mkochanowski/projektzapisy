import * as React from "react";
import * as ReactDOM from "react-dom";

import { whenDomLoaded } from "common/utils";

function main() {
	console.warn("Theses system: React main");
	ReactDOM.render(
		<h1>Hello, world!</h1>,
		document.getElementById("theses-react-root"),
	);
}
whenDomLoaded(main);
