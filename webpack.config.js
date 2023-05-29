const path = require("path");
const autoprefixer = require("autoprefixer");
const cssnano = require("cssnano");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const postcssCustomProperties = require("postcss-custom-properties");
const sass = require("sass");
const ESLintPlugin = require("eslint-webpack-plugin");
const StylelintPlugin = require("stylelint-webpack-plugin");

const projectRoot = "src/web";

const options = {
  entry: {
    // multiple entries can be added here
    main: `./${projectRoot}/js/main.js`,
  },
  output: {
    path: path.resolve(__dirname, "public/"),
    // based on entry name, e.g. main.js
    filename: "js/[name].min.js", // based on entry name, e.g. main.js
    clean: false,
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "css/[name].min.css",
    }),
    new ESLintPlugin({
      failOnError: false,
      lintDirtyModulesOnly: true,
      emitWarning: true,
    }),
    new StylelintPlugin({
      failOnError: false,
      lintDirtyModulesOnly: true,
      emitWarning: true,
      extensions: ["scss"],
    }),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
      {
        // this will apply to `.scss` files
        test: /\.(scss|css)$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: "css-loader",
            options: {
              sourceMap: true,
            },
          },
          {
            loader: "postcss-loader",
            options: {
              sourceMap: true,
              postcssOptions: {
                plugins: () => [
                  autoprefixer(),
                  postcssCustomProperties(),
                  cssnano({
                    preset: "default",
                  }),
                ],
              },
            },
          },
          {
            loader: "sass-loader",
            options: {
              sourceMap: true,
              implementation: sass,
              sassOptions: {
                outputStyle: "compressed",
              },
            },
          },
        ],
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: "asset/resource",
        generator: {
          filename: "fonts/[name][ext]",
        },
      },
    ],
  },
};

const webpackConfig = (environment, argv) => {
  const isProduction = argv.mode === "production";

  options.mode = isProduction ? "production" : "development";

  if (!isProduction) {
    // https://webpack.js.org/configuration/stats/
    const stats = {
      // Tells stats whether to add the build date and the build time information.
      builtAt: false,
      // Add chunk information (setting this to `false` allows for a less verbose output)
      chunks: false,
      // Add the hash of the compilation
      hash: false,
      // `webpack --colors` equivalent
      colors: true,
      // Add information about the reasons why modules are included
      reasons: false,
      // Add webpack version information
      version: false,
      // Add built modules information
      modules: false,
      // Show performance hint when file size exceeds `performance.maxAssetSize`
      performance: false,
      // Add children information
      children: false,
      // Add asset Information.
      assets: false,
    };

    options.stats = stats;

    // Create JS source maps in the dev mode
    // See https://webpack.js.org/configuration/devtool/ for more options
    options.devtool = "inline-source-map";
  }

  return options;
};

module.exports = webpackConfig;
