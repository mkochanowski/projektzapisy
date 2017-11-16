import * as $ from "jquery";

function scrollUpToElementIfWindowBelow(selector) {
	const SCROL_TIME = 400;
	const currentWindowTop = $(window).scrollTop();
	const elemTop = $(selector).offset().top;
	if (currentWindowTop > elemTop) {
		$("html, body").animate({ scrollTop: elemTop }, SCROL_TIME);
	}
}

export { scrollUpToElementIfWindowBelow };
