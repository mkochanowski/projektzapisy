// Common utility functions shared between apps
import * as $ from "jquery";
import { UnconstrainedFunction } from "./types";

export function scrollUpToElementIfWindowBelow(selector: string) {
	const SCROL_TIME = 400;
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
		$("html, body")!.animate({ scrollTop: elemTop }, SCROL_TIME);
	}
}

// TODO make sure this is correct - differences between browsers etc
export function whenDomLoaded(cb: UnconstrainedFunction): void {
	window.addEventListener("DOMContentLoaded", cb);
}
