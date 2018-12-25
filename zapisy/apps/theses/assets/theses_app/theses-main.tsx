/*
	The entry point to the theses React app.
	The only purpose of this file is to bootstrap the app by rendering
	the root component after the page loads, having first wrapped it in
	an error boundary to catch any escaped errors and handle them in
	a (mostly) graceful manner.
*/

import * as React from "react";
import * as ReactDOM from "react-dom";

import { whenDomLoaded } from "common/utils";
import { ThesesApp } from "./components/ThesesApp";
import { ErrorBoundary } from "./components/ErrorBoundary";

function main() {
	ReactDOM.render(
		<ErrorBoundary>
			<ThesesApp/>
		</ErrorBoundary>,
		document.getElementById("theses-react-root"),
	);
}
whenDomLoaded(main);
