const path = require("path");
const pluginRss = require("@11ty/eleventy-plugin-rss");

// const searchFilter = require("./app/utils/searchFilter.js");

module.exports = (eleventyConfig) => {
  // Plugins
  eleventyConfig.addPlugin(pluginRss);

  // Collections
  eleventyConfig.addCollection("news", function (collectionApi) {
    return collectionApi.getFilteredByTag("news").sort((a, b) => {
      return new Date(b.date) - new Date(a.date); // Sort by date, newest first
    });
  });

  // Date filters
  eleventyConfig.addFilter("date", function (dateObj, format) {
    const date = new Date(dateObj);

    if (format === "YYYY-MM-DD") {
      return date.toISOString().split("T")[0];
    }
    if (format === "dddd, MMMM Do, YYYY") {
      return date.toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    }
    if (format === "dddd") {
      return date.toLocaleDateString("en-US", { weekday: "long" });
    }
    if (format === "MMMM Do, YYYY") {
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    }
    if (format === "MMM DD, YYYY") {
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "2-digit",
      });
    }
    if (format.includes("[at]") && format.includes("h:mm A")) {
      // Handle formats like "MMMM Do, YYYY [at] h:mm A [UTC]"
      const datePart = date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
      const timePart = date.toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      });
      return `${datePart} at ${timePart} UTC`;
    }

    // Default format
    return date.toLocaleDateString("en-US");
  });

  // TODO: Add Search Filter
  // eleventyConfig.addFilter("search", searchFilter);

  // Handle newlines in content
  eleventyConfig.addFilter("nl2p", function (content) {
    if (!content) return "";

    // Split content by double newlines (paragraph breaks)
    const paragraphs = content.trim().split(/\n\s*\n/);

    // Wrap each paragraph in <p> tags and join
    return paragraphs
      .filter((p) => p.trim().length > 0) // Remove empty paragraphs
      .map((p) => `<p>${p.trim()}</p>`)
      .join("\n\n");
  });

  // Add Shortcodes
  // Get the current year - super useful for copyright dates.
  eleventyConfig.addShortcode("year", () => `${new Date().getFullYear()}`);

  // Template formats
  eleventyConfig.setTemplateFormats(["md", "njk", "html"]);

  // Copy favicons & images
  eleventyConfig.addPassthroughCopy({ "app/web/ico": "ico" });
  eleventyConfig.addPassthroughCopy({ "app/web/img": "img" });

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

  // You can return your Config object (optional).
  return {
    dir: {
      input: "app/web",
      output: "public",
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};
