import * as React from "react";
import ReactTable from "react-table";
import "react-table/react-table.css";
import { ThesesList } from "./ThesesList";
import { Thesis } from "../types";
import { getThesesList, ThesisTypeFilter } from "../backend_callers";

export class ThesesApp extends React.Component<{}> {
	render() {
		return [
			<h2 key="title">Prace dyplomowe</h2>,
			<hr key="divider"/>,
			<div key="container" style={{ margin: "0 auto" }}>
				<ThesesList />
			</div>
		];
	}
}
