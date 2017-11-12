module.exports = {
	bundles: {
		"course-details": [
			"enrollment/courses/courseDetailsTest.ts",
			"enrollment/courses/testStyle.less"
		]
	},
	rawfiles: [
		{ src: "legacy_assets/css/", dest: "css/" },
		{ src: "legacy_assets/help/", dest: "help/" },
		{ src: "legacy_assets/images/", dest: "images/" },
		{ src: "legacy_assets/js/", dest: "js/" },
		{ src: "legacy_assets/vendor/", dest: "vendor/" },
		{ src: "legacy_assets/favicon.ico", dest: "favicon.ico" },
		{ src: "legacy_assets/feed-icon.png", dest: "feed-icon.png" }
	],
	otherDefs: [
		"./apps/enrollment/courses/asset-defs",
	],
};
