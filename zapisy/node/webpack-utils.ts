const ExtractTextPlugin = require("extract-text-webpack-plugin");

function getVueCssLoaders(options: any) {
	// generate loader string to be used with extract text plugin
	function generateLoaders (loaders: Array<string>) {
	  	let sourceLoader = loaders.map(function (loader: string) {
			let extraParamChar;
			if (/\?/.test(loader)) {
				loader = loader.replace(/\?/, "-loader?");
				extraParamChar = "&";
			} else {
				loader = loader + "-loader";
				extraParamChar = "?";
			}
			return loader + (options.sourceMap ? extraParamChar + "sourceMap" : "");
	  	}).join("!");

		// Extract CSS when that option is specified
		// (which is the case during production build)
		if (options.extract) {
			return ExtractTextPlugin.extract("vue-style-loader", sourceLoader);
	  	} else {
			return ["vue-style-loader", sourceLoader].join("!");
		}
	}

	// http://vuejs.github.io/vue-loader/en/configurations/extract-css.html
	return {
		css: generateLoaders(["css"]),
		postcss: generateLoaders(["css"]),
		less: generateLoaders(["css", "less"]),
	};
}

export { getVueCssLoaders };
