module.exports = {
	rawfiles: [
		{ from: "./assets/legacy/css/", to: "css/" },
		{ from: "./assets/legacy/help/", to: "help/" },
		{ from: "./assets/legacy/images/", to: "images/" },
		{ from: "./assets/legacy/js/", to: "js/" },
		{ from: "./assets/legacy/vendor/", to: "vendor/" },
		{ from: "./assets/legacy/favicon.ico", to: "favicon.ico" },
		{ from: "./assets/legacy/feed-icon.png", to: "feed-icon.png" }
	],
	otherDefs: [
		"./apps/enrollment/courses/asset-defs",
	],
};
