import * as React from "react";

import styled from "styled-components";
import {
	Thesis, ThesisKind, Employee, Student,
	MAX_THESIS_TITLE_LEN, AppUser,
} from "../../../types";
import { PersonType } from "../../../backend_callers";
import { PersonField } from "./PersonField";
import { ThesisKindField } from "./ThesisKindField";
import { AddRemoveIcon, IconType } from "./AddRemoveIcon";
import { canSetArbitraryAdvisor, canModifyThesis, canChangeTitle } from "../../../permissions";

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

const OptionalFieldLabel = React.memo(styled.span`
	font-style: italic;
`);

type State = {
	displayAuxAdvisor: boolean;
	displayAuxStudent: boolean;
};

type Props = {
	thesis: Thesis;
	/** Should the title field be highlighted to indicate an error? */
	titleError: boolean;
	user: AppUser;
	onTitleChanged: (nt: string) => void;
	onKindChanged: (nk: ThesisKind) => void;
	onAdvisorChanged: (na: Employee | null) => void;
	onAuxAdvisorChanged: (na: Employee | null) => void;
	onStudentChanged: (na: Student | null) => void;
	onSecondStudentChanged: (na: Student | null) => void;
	onDescriptionChanged: (nd: string) => void;
};

/** Decide whether to display the fields based on the thesis instance in the props */
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
		const readOnly = !canModifyThesis(this.props.user, this.props.thesis);

		return <div>
			<MidFormTable>
				<tbody>
				{this.renderTitle(readOnly)}
				{this.renderKind(readOnly)}
				{this.renderAdvisors(readOnly)}
				{this.renderStudents(readOnly)}
				</tbody>
			</MidFormTable>
			{this.renderDescription(readOnly)}
		</div>;
	}

	private renderTitle(readOnly: boolean) {
		const titleStyle: React.CSSProperties = {
			width: "100%",
			height: "70px",
			boxSizing: "border-box",
		};
		if (this.props.titleError) {
			Object.assign(titleStyle, {
				border: "1px solid red"
			});
		}
		const titleReadOnly = readOnly || !canChangeTitle(this.props.user, this.props.thesis);
		return <tr>
			<td>Tytuł</td>
			<td><textarea
				style={titleStyle}
				value={this.props.thesis.title}
				maxLength={MAX_THESIS_TITLE_LEN}
				readOnly={titleReadOnly}
				onChange={ev => this.props.onTitleChanged(ev.target.value)}
			/></td>
		</tr>;
	}

	private renderKind(readOnly: boolean) {
		return <tr>
			<td>Typ</td>
			<td>
				<ThesisKindField
					value={this.props.thesis.kind}
					readOnly={readOnly}
					onChange={this.props.onKindChanged}
				/>
			</td>
		</tr>;
	}

	private renderAdvisors(readOnly: boolean) {
		return <>
			<tr>
				<td>Promotor</td>
				<td>
					<PersonField
						personType={PersonType.Employee}
						onChange={this.props.onAdvisorChanged}
						value={this.props.thesis.advisor}
						readOnly={readOnly || !canSetArbitraryAdvisor(this.props.user)}
					/>
					{ readOnly
						? null
						: <AddRemoveIcon
							onClick={this.triggerAuxAdvVisibility}
							type={this.state.displayAuxAdvisor ? IconType.Remove : IconType.Add}
						/>
					}
				</td>
			</tr>
			{ this.state.displayAuxAdvisor ? (
				<tr>
					<td><OptionalFieldLabel>Promotor wspomagający</OptionalFieldLabel></td>
					<td>
						<PersonField
							personType={PersonType.Employee}
							onChange={this.props.onAuxAdvisorChanged}
							value={this.props.thesis.auxiliaryAdvisor}
							readOnly={readOnly}
						/>
					</td>
				</tr>
			) : null }
		</>;
	}

	private renderStudents(readOnly: boolean) {
		return <>
			<tr>
				<td>Student</td>
				<td>
					<PersonField
						personType={PersonType.Student}
						onChange={this.props.onStudentChanged}
						value={this.props.thesis.student}
						readOnly={readOnly}
					/>
					{ readOnly
						? null
						: <AddRemoveIcon
							onClick={this.triggerSecondStudentVisibility}
							type={this.state.displayAuxStudent ? IconType.Remove : IconType.Add}
						/>
					}
				</td>
			</tr>
			{ this.state.displayAuxStudent ? (
				<tr>
					<td><OptionalFieldLabel>Student wspomagający</OptionalFieldLabel></td>
					<td>
						<PersonField
							personType={PersonType.Student}
							onChange={this.props.onSecondStudentChanged}
							value={this.props.thesis.secondStudent}
							readOnly={readOnly}
						/>
					</td>
				</tr>
			) : null }
		</>;
	}

	private renderDescription(readOnly: boolean) {
		return <textarea
			style={{ width: "100%", height: "100px", boxSizing: "border-box" }}
			value={this.props.thesis.description}
			readOnly={readOnly}
			onChange={this.handleDescriptionChanged}
		/>;
	}
}
