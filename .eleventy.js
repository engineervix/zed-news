const path = require("path");
const htmlmin = require("html-minifier");
const pluginRss = require("@11ty/eleventy-plugin-rss");

// const searchFilter = require("./src/utils/searchFilter.js");

module.exports = (eleventyConfig) => {
  // Plugins
  eleventyConfig.addPlugin(pluginRss);

  // TODO: Add Search Filter
  // eleventyConfig.addFilter("search", searchFilter);

  // Add Shortcodes
  // Get the current year - super useful for copyright dates.
  eleventyConfig.addShortcode("year", () => `${new Date().getFullYear()}`);

  // Template formats
  eleventyConfig.setTemplateFormats(["md", "njk", "html"]);

  // Copy favicons & images
  eleventyConfig.addPassthroughCopy({ "src/web/ico": "ico" });
  eleventyConfig.addPassthroughCopy({ "src/web/img": "img" });

  // Tell 11ty to use the .eleventyignore and ignore our .gitignore file
  eleventyConfig.setUseGitIgnore(false);

  // Add delay before re-running
  eleventyConfig.setWatchThrottleWaitTime(500); // in milliseconds

  // dev server
  eleventyConfig.setServerOptions({
    watch: [
      path.resolve(__dirname, "public/js/**/*.js"),
      path.resolve(__dirname, "public/css/**/*.css"),
    ],
    showVersion: true,
  });

  if (process.env.ELEVENTY_ENV === "production") {
    eleventyConfig.addTransform("htmlmin", (content, outputPath) => {
      if (outputPath.endsWith(".html")) {
        const minified = htmlmin.minify(content, {
          collapseInlineTagWhitespace: false,
          collapseWhitespace: true,
          removeComments: true,
          sortClassName: true,
          useShortDoctype: true,
        });

        return minified;
      }

      return content;
    });
  }

  // You can return your Config object (optional).
  return {
    dir: {
      input: "src/web",
      output: "public",
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};
