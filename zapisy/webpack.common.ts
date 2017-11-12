import * as path from "path";
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const UglifyJSPlugin = require("uglifyjs-webpack-plugin");
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const CleanWebpackPlugin = require("clean-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");

const BUNDLE_TARGET_DIR = "asset_bundles";

// the path(s) that should be cleaned
const pathsToClean = [
	`${BUNDLE_TARGET_DIR}/`
];

// the clean options to use
const cleanOptions = {
	verbose:  true,
	dry:      false
};

type RawfileDef = {
	src: string,
	dest: string
};

type AssetDefs = {
	bundles?: {
		[key: string]: Array<string>
	},
	rawfiles?: Array<RawfileDef>
};

function importDefs(fileName: string): AssetDefs {
	const dirPath = path.dirname(fileName);
	const dirName = path.basename(dirPath);
	const defs: AssetDefs = require(fileName);
	const result: AssetDefs = {
		bundles: {},
		rawfiles: [],
	};
	const getFullInputPath = inputPath => "./" + path.join(dirPath, inputPath);
	for (const bundleName in defs.bundles || {}) {
		const fullBundleName = `${dirName}-${bundleName}`;
		const fullBundlePaths = defs.bundles[bundleName].map(bundlePath => {
			return getFullInputPath(bundlePath);
		});
		result.bundles[fullBundleName] = fullBundlePaths;
	}
	if (defs.rawfiles) {
		const getRawfileOutputPath = rawfilePath => {
			return path.join(dirName, rawfilePath);
		};
		result.rawfiles = defs.rawfiles.map(rawfileDef => {
			return {
				src: getFullInputPath(rawfileDef.src),
				dest: getRawfileOutputPath(rawfileDef.dest)
			};
		});
	}
	return result;
}

function getAllAssetDefs() {
	const globalDefs = require("./asset-defs");
	const result = {
		bundles: globalDefs.bundles || {},
		rawfiles: globalDefs.rawfiles || [],
	};
	for (const defPath of globalDefs.otherDefs) {
		const def = importDefs(defPath);
		Object.assign(result.bundles, def.bundles);
		result.rawfiles = result.rawfiles.concat(def.rawfiles);
	}
	return result;
}

function isExternal(module) {
	const context = module.context;

	if (typeof context !== "string") {
		return false;
	}

	return context.indexOf("node_modules") !== -1;
}

const allAssetDefs = getAllAssetDefs();
console.log(allAssetDefs);
module.exports = function(config) {
	return {
		entry: allAssetDefs.bundles,
		output: {
			path: path.resolve(`./${BUNDLE_TARGET_DIR}/`),
			filename: "[name]-[hash].min.js"
		},
		module: {
			rules: [
				// TypeScript source:
				// 1) tsc: TS -> ES6
				// 2) babel: ES6 -> ES5 (and polyfilling)
				{
					test: /\.ts?$/,
					loaders: ["babel-loader", "ts-loader"],
					exclude: /node_modules/
				},
				// ES6 source: babel converts to ES5 (and polyfills)
				{
					test: /\.js?$/,
					loader: "babel-loader",
					exclude: /node_modules/
				},
				{
					test: /\.less$/,
					use: ExtractTextPlugin.extract({
						fallback: "style-loader",
						use: [{
							loader: "css-loader",
							options: { minimize: config.minifyCss }
						}, {
							loader: "less-loader"
						}]
					})
				}
			]
		},
		resolve: {
			extensions: [".ts", ".js"]
		},
		plugins: [
			new webpack.optimize.CommonsChunkPlugin({
				name: "vendor",
				filename: "vendor.js",
				minChunks: function(module) {
					return isExternal(module);
				}
			}),
			new CleanWebpackPlugin(pathsToClean, cleanOptions),
			new ExtractTextPlugin("[name]-[hash].min.css", {
				allChunks: true
			}),
			new BundleTracker({ filename: "./webpack-stats.json" }),
			// This will copy "raw" assets - ones where we don't want any transformations
			// (e.g. bootstrap styles)
			new CopyWebpackPlugin(allAssetDefs.rawfiles),
		]
	};
};
