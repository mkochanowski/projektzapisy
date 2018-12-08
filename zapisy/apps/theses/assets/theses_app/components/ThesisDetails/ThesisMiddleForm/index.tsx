import * as React from "react";

import styled from "styled-components";
import { Thesis, ThesisKind, Employee, Student, MAX_THESIS_TITLE_LEN } from "../../../types";
import { PersonType } from "../../../backend_callers";
import { PersonSelect } from "./PersonSelect";
import { ThesisKindSelect } from "./ThesisKindSelect";
import { AddRemoveIcon, IconType } from "./AddRemoveIcon";

const MidFormTable = styled.table`
	width: 100%;

	td {
		border-left: 4px solid transparent;
		border-top: 6px solid transparent;
	}
	td:first-child {
		border-left: 0;
	}
	tr:first-child td {
		border-top: 0;
	}

	tr td:first-child {
		width: 13%;
	}
`;

const OptionalFieldLabel = styled.span`
font-style: italic;
`;

type State = {
	displayAuxAdvisor: boolean;
	displayAuxStudent: boolean;
};

type Props = {
	thesis: Thesis;
	titleError: boolean;
	onTitleChanged: (nt: string) => void;
	onKindChanged: (nk: ThesisKind) => void;
	onAdvisorChanged: (na: Employee | null) => void;
	onAuxAdvisorChanged: (na: Employee | null) => void;
	onStudentChanged: (na: Student | null) => void;
	onSecondStudentChanged: (na: Student | null) => void;
	onDescriptionChanged: (nd: string) => void;
};

function getStateFromProps(props: Props) {
	return {
		displayAuxAdvisor: props.thesis.auxiliaryAdvisor !== null,
		displayAuxStudent: props.thesis.secondStudent !== null,
	};
}

export class ThesisMiddleForm extends React.PureComponent<Props, State> {
	constructor(props: Props) {
		super(props);
		this.state = getStateFromProps(props);
	}

	public UNSAFE_componentWillReceiveProps(nextProps: Props) {
		this.setState(getStateFromProps(nextProps));
	}

	private handleDescriptionChanged = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		this.props.onDescriptionChanged(e.target.value);
	}

	private triggerAuxAdvVisibility = () => {
		const newValue = !this.state.displayAuxAdvisor;
		this.setState({ displayAuxAdvisor: newValue });
		if (!newValue) {
			this.props.onAuxAdvisorChanged(null);
		}
	}

	private triggerSecondStudentVisibility = () => {
		const newValue = !this.state.displayAuxStudent;
		this.setState({ displayAuxStudent: newValue });
		if (!newValue) {
			this.props.onSecondStudentChanged(null);
		}
	}

	public render() {
		const titleStyle: React.CSSProperties = { width: "100%", height: "70px", boxSizing: "border-box" };
		if (this.props.titleError) {
			Object.assign(titleStyle, {
				border: "1px solid red"
			});
		}
		return <div>
			<MidFormTable>
				<tbody>
				<tr>
					<td>Tytuł</td>
					<td><textarea
						style={titleStyle}
						value={this.props.thesis.title}
						maxLength={MAX_THESIS_TITLE_LEN}
						onChange={ev => this.props.onTitleChanged(ev.target.value)}
					/></td>
				</tr>
				<tr>
					<td>Typ</td>
					<td>
						<ThesisKindSelect
							value={this.props.thesis.kind}
							onChange={this.props.onKindChanged}
						/>
					</td>
				</tr>
				<tr>
					<td>Promotor</td>
					<td>
						<PersonSelect
							personType={PersonType.Employee}
							onChange={this.props.onAdvisorChanged}
							value={this.props.thesis.advisor}
						/>
						<AddRemoveIcon
							onClick={this.triggerAuxAdvVisibility}
							type={this.state.displayAuxAdvisor ? IconType.Remove : IconType.Add}
						/>
					</td>
				</tr>
				{ this.state.displayAuxAdvisor ? (
					<tr>
						<td><OptionalFieldLabel>Promotor wspomagający</OptionalFieldLabel></td>
						<td>
							<PersonSelect
								personType={PersonType.Employee}
								onChange={this.props.onAuxAdvisorChanged}
								value={this.props.thesis.auxiliaryAdvisor}
							/>
						</td>
					</tr>
				) : null }
				<tr>
					<td>Student</td>
					<td>
						<PersonSelect
							personType={PersonType.Student}
							onChange={this.props.onStudentChanged}
							value={this.props.thesis.student}
						/>
						<AddRemoveIcon
							onClick={this.triggerSecondStudentVisibility}
							type={this.state.displayAuxStudent ? IconType.Remove : IconType.Add}
						/>
					</td>
				</tr>
				{ this.state.displayAuxStudent ? (
					<tr>
						<td><OptionalFieldLabel>Student wspomagający</OptionalFieldLabel></td>
						<td>
							<PersonSelect
								personType={PersonType.Student}
								onChange={this.props.onSecondStudentChanged}
								value={this.props.thesis.secondStudent}
							/>
						</td>
					</tr>
				) : null }
				</tbody>
			</MidFormTable>
			<textarea
				style={{ width: "100%", height: "100px", boxSizing: "border-box" }}
				value={this.props.thesis.description}
				onChange={this.handleDescriptionChanged}
			/>
		</div>;
	}
}
