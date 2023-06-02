require("dotenv").config();

const environment = process.env.ELEVENTY_ENV;
const PROD_ENV = "production";
const isProd = environment === PROD_ENV;

module.exports = {
  isProd,
  base_url: process.env.BASE_URL,
  builtAt: new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "numeric",
    timeZone: "Africa/Lusaka",
    timeZoneName: "short",
  }).format(new Date()),
  articlesBySource: function (articles) {
    const articlesBySource = {};
    articles.forEach((article) => {
      const source = article.source;
      if (!articlesBySource[source]) {
        articlesBySource[source] = [];
      }
      articlesBySource[source].push(article);
    });
    return articlesBySource;
  },
};
