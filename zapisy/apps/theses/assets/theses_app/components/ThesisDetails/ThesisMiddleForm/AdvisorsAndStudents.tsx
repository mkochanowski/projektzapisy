import * as React from "react";
import styled from "styled-components";

import { PersonType } from "../../../backend_callers";
import { PersonField } from "./PersonField";
import { Employee, Student, AppUser } from "../../../types";
import { AddRemoveIcon, IconType } from "./AddRemoveIcon";
import { canSetArbitraryAdvisor } from "../../../permissions";

type Props = {
	user: AppUser;
	readOnly: boolean;
	advisor: Employee | null;
	auxAdvisor: Employee | null;
	student: Student | null;
	secondStudent: Student | null;
	onAdvisorChanged: (na: Employee | null) => void;
	onAuxAdvisorChanged: (na: Employee | null) => void;
	onStudentChanged: (na: Student | null) => void;
	onSecondStudentChanged: (na: Student | null) => void;
};

const initialState = {
	displayAuxAdvisor: false,
	displayAuxStudent: false,
};
type State = typeof initialState;

const OptionalFieldLabel = styled.span`
	font-style: italic;
`;

export class AdvisorsAndStudents extends React.PureComponent<Props, State> {
	state = initialState;
	public render() {
		return <>
			{this.renderAdvisors()}
			{this.renderStudents()}
		</>;
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

	private renderAdvisors() {
		const { readOnly } = this.props;
		return <>
			<tr>
				<td>Promotor</td>
				<td>
					<PersonField
						personType={PersonType.Employee}
						onChange={this.props.onAdvisorChanged}
						value={this.props.advisor}
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
							value={this.props.auxAdvisor}
							readOnly={readOnly}
						/>
					</td>
				</tr>
			) : null }
		</>;
	}

	private renderStudents() {
		const { readOnly } = this.props;
		return <>
			<tr>
				<td>Student</td>
				<td>
					<PersonField
						personType={PersonType.Student}
						onChange={this.props.onStudentChanged}
						value={this.props.student}
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
							value={this.props.secondStudent}
							readOnly={readOnly}
						/>
					</td>
				</tr>
			) : null }
		</>;
	}
}
