// Common utility functions shared between apps
import * as $ from "jquery";
import { UnconstrainedFunction } from "./types";

const SCROLL_TIME = 400;
export function scrollUpToElementIfWindowBelow(selector: string): void {
	const currentWindowTop = $(window).scrollTop();
	if (!currentWindowTop) {
		return;
	}
	const elem = $(selector);
	if (!elem) {
		throw new Error(`Unable to find ${selector}`);
	}
	const elemTop = elem.offset()!.top;
	if (currentWindowTop > elemTop) {
		$("html, body").animate({ scrollTop: elemTop }, SCROLL_TIME);
	}
}

export function whenDomLoaded(fn: UnconstrainedFunction): void {
	if (document.readyState !== "loading") {
		fn();
	} else {
		window.addEventListener("DOMContentLoaded", fn);
	}
}

export function awaitSleep(ms: number): Promise<void> {
	return new Promise((resolve, _) => {
		window.setTimeout(resolve, ms);
	});
}

export function strcmp(a: string, b: string) {
	return (a < b ? -1 : (a > b ? 1 : 0));
}

export function inRange<T>(value: T, min: T, max: T): boolean {
	return value >= min && value <= max;
}

export type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
