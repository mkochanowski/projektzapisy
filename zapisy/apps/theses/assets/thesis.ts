/**
 * @file Defines the Thesis class and associated types
 */
import * as moment from "moment";
import { Employee, Student, Person } from "./users";
import { ThesisKind, ThesisStatus } from "./protocol_types";
import { nullableValuesEqual } from "./utils";

export const MAX_THESIS_TITLE_LEN = 300;
export const MAX_RESERVATION_YEARS = 10;

/**
 * Native representation of a thesis
 */
export class Thesis {
	public id: number;
	public title: string;
	public advisor: Employee | null;
	public auxiliaryAdvisor: Employee | null;
	public kind: ThesisKind;
	public reservedUntil: moment.Moment | null;
	public description: string;
	public status: ThesisStatus;
	public student: Student | null;
	public secondStudent: Student | null;
	public modifiedDate: moment.Moment;

	/** Construct a new thesis object with default values */
	public constructor() {
		this.id = -1;
		this.title = "";
		this.advisor = null;
		this.auxiliaryAdvisor = null;
		this.kind = ThesisKind.Bachelors;
		this.reservedUntil = null;
		this.description = "";
		this.status = ThesisStatus.BeingEvaluated;
		this.student = null;
		this.secondStudent = null;
		this.modifiedDate = moment();
	}

	/**
	 * Determine whether this thesis is archived, i.e. has been defended
	 */
	public isArchived() {
		return this.status === ThesisStatus.Defended;
	}

	/**
	 * Is this the same thesis as the supplied one?
	 * @param other The other thesis
	 * Note that because this is a fat arrow it can be conveniently used
	 * as a callback, i.e. theses.find(t.isEqual)
	 */
	public isEqual = (other: Thesis): boolean => {
		return this.id === other.id;
	}

	/**
	 * Determine whether the other instance of the same thesis has been modified;
	 * to compare two possibly different thesis objects, see isEqual above
	 * @param other The other thesis
	 */
	public areValuesEqual(other: Thesis): boolean {
		console.assert(
			this.isEqual(other),
			"Thesis::areValuesEqual only makes sense for two theses with the same ID",
		);
		return (
			this.title === other.title &&
			this.description === other.description &&
			nullableValuesEqual(this.advisor, other.advisor, personCompare) &&
			nullableValuesEqual(this.auxiliaryAdvisor, other.auxiliaryAdvisor, personCompare) &&
			nullableValuesEqual(this.student, other.student, personCompare) &&
			nullableValuesEqual(this.secondStudent, other.secondStudent, personCompare) &&
			this.kind === other.kind &&
			this.isReservationDateSame(other.reservedUntil) &&
			this.status === other.status &&
			this.modifiedDate.isSame(other.modifiedDate)
		);
	}

	public isReservationDateSame(otherDate: moment.Moment | null) {
		return nullableValuesEqual(this.reservedUntil, otherDate, (d1, d2) => d1.isSame(d2));
	}

	public getMaxReservationDate() {
		return moment().add(MAX_RESERVATION_YEARS, "years");
	}
}

function personCompare(p1: Person, p2: Person) {
	return p1.isEqual(p2);
}
