import { UserType } from "./protocol_types";

/**
 * Represents a person in the thesis system
 */
export class Person {
	public id: number;
	public displayName: string;

	public constructor(id: number, displayName: string) {
		this.id = id;
		this.displayName = displayName;
	}

	public isEqual = (other: Person): boolean => {
		return this.id === other.id;
	}
}

// The next two classes have the same shape (for now at least), but
// they are disparate types and should not be interchangeable, but thanks
// to TS's structural typing they are. To get around that
// we add a hidden private property to make the types incompatible
// tslint:disable:variable-name
/**
 * Represents a university employee in the thesis system
 */
export class Employee extends Person {
	// @ts-ignore
	private __nominal: void;
}
/**
 * Represents a student in the thesis system
 */
export class Student extends Person {
	// @ts-ignore
	private __nominal: void;
}
// tslint:enable:variable-name

/**
 * Represents the user of the thesis system
 */
export class AppUser {
	public user: Person;
	public type: UserType;

	public constructor(user: Person, type: UserType) {
		this.user = user;
		this.type = type;
	}
}
