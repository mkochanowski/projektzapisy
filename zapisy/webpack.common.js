const path = require('path');
const webpack = require("webpack");
const BundleTracker = require('webpack-bundle-tracker');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const CleanWebpackPlugin = require('clean-webpack-plugin');
const CopyWebpackPlugin = require("copy-webpack-plugin");
const assetDefs = require("./asset-defs.js");

const BUNDLE_SOURCE_DIR = "assets";
const BUNDLE_TARGET_DIR = "asset_bundles";

// the path(s) that should be cleaned
const pathsToClean = [
  `${BUNDLE_TARGET_DIR}/`,
];

// the clean options to use
const cleanOptions = {
  verbose:  true,
  dry:      false
}

function processBundles(bundles) {
  const result = {};
  for (const bundleName in bundles) {
    const fileList = bundles[bundleName].map(fileName => {
      return `./${BUNDLE_SOURCE_DIR}/${fileName}`;
    });
    result[bundleName] = fileList;
  }
  return result;
}

function processRawfiles(rawfiles) {
  return rawfiles.map(rawfile => {
    if (typeof rawfile === "string") {
      return {
        from: `./${BUNDLE_SOURCE_DIR}/${rawfile}`,
        to: rawfile,
      };
    }
    return {
      from: `./${BUNDLE_SOURCE_DIR}/${rawfile.src}`,
      to: rawfile.dest,
    };
  });
}

function isExternal(module) {
  const context = module.context;

  if (typeof context !== 'string') {
    return false;
  }

  return context.indexOf('node_modules') !== -1;
}

module.exports = function(config) {
  return {
    context: __dirname,
    entry: processBundles(assetDefs.bundles),
    output: {
        path: path.resolve(`./${BUNDLE_TARGET_DIR}/`),
        filename: "[name]-[hash].min.js",
    },
    module: {
      rules: [
          // TypeScript source:
          // 1) tsc: TS -> ES6
          // 2) babel: ES6 -> ES5 (and polyfilling)
          {
              test: /\.ts?$/,
              loaders: ['babel-loader', 'ts-loader'],
              exclude: /node_modules/,
          },
          // ES6 source: babel converts to ES5 (and polyfills)
          {
            test: /\.js?$/,
            loader: 'babel-loader',
            exclude: /node_modules/,
          },
          {
              test: /\.less$/,
              use: ExtractTextPlugin.extract({
                fallback: "style-loader",
                use: [{
                  loader: "css-loader",
                  options: { minimize: config.minifyCss },
                }, {
                  loader: "less-loader",
                }],
              }),
          },
      ]
    },
    resolve: {
      extensions: [".ts", ".js"],
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
      new BundleTracker({filename: './webpack-stats.json'}),
      // This will copy "raw" assets - ones where we don't want any transformations
      // (e.g. bootstrap styles)
      new CopyWebpackPlugin(processRawfiles(assetDefs.rawfiles)),
    ]
  }
};
