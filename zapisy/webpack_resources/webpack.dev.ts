const SpeedMeasurePlugin = require("speed-measure-webpack-plugin");

const smp = new SpeedMeasurePlugin();
const merge = require("webpack-merge");
const common = require("./webpack.common.ts");

module.exports = smp.wrap(merge(common({
	minifyCss: false,
	vueCssOptions: {
		sourceMap: true,
		extract: false,
	}
}), {
	devtool: "inline-source-map"
}));
