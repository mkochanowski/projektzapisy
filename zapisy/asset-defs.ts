module.exports = {
	bundles: {
		"courses-course-details":
		[
			"./assets/test.ts",
		],
	},
	rawfiles: [
		{ src: "assets/legacy/css/", dest: "css/" },
		{ src: "assets/legacy/help/", dest: "help/" },
		{ src: "assets/legacy/images/", dest: "images/" },
		{ src: "assets/legacy/js/", dest: "js/" },
		{ src: "assets/legacy/vendor/", dest: "vendor/" },
		{ src: "assets/legacy/favicon.ico", dest: "favicon.ico" },
		{ src: "assets/legacy/feed-icon.png", dest: "feed-icon.png" }
	],
	otherDefs: [
		// "./apps/enrollment/courses/asset-defs",
	],
};
