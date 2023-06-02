require("dotenv").config();

const environment = process.env.ELEVENTY_ENV;
const PROD_ENV = "production";
const isProd = environment === PROD_ENV;

module.exports = {
  isProd,
  base_url: process.env.BASE_URL,
  contact_email: process.env.CONTACT_EMAIL,
  analytics_id: process.env.UMAMI_SITE_ID,
  analytics_url: process.env.UMAMI_URL,
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
