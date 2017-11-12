const merge = require("webpack-merge");
const common = require("./webpack.common.ts");

module.exports = merge(common({
	minifyCss: false
}), {
	devtool: "inline-source-map"
});
