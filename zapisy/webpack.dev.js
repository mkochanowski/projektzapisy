const merge = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common({
	minifyCss: false,
	}), {
	devtool: 'inline-source-map',
});
