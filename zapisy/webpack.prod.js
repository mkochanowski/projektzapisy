const merge = require('webpack-merge');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const common = require('./webpack.common.js');

module.exports = merge(common({
	minifyCss: true,
}), {
	plugins: [
		new UglifyJSPlugin({
			sourceMap: true,
			compress: true,
			output: {comments: false},
			comments: false,
		}),
	],
});

