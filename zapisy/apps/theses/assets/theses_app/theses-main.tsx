import * as React from "react";
import * as ReactDOM from "react-dom";

import { whenDomLoaded } from "common/utils";
import { ThesesApp } from "./components/ThesesApp";
import { ErrorBoundary } from "./components/ErrorBoundary";
import "./debug";

function main() {
	ReactDOM.render(
		<ErrorBoundary>
			<ThesesApp/>
		</ErrorBoundary>,
		document.getElementById("theses-react-root"),
	);
}
whenDomLoaded(main);
