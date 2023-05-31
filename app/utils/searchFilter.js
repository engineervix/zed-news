const elasticlunr = require("elasticlunr-dev");
const { base_url } = require("../web/_data/site");

module.exports = function (collection) {
  // what fields we'd like our index to consist of
  const index = elasticlunr(function () {
    this.addField("title");
    this.addField("description");
    this.setRef("id");
  });

  // loop through each page and add it to the index
  collection.forEach((page) => {
    index.addDoc({
      id: base_url + page.url,
      title: page.template.frontMatter.data.title,
      description: page.template.frontMatter.data.description,
    });
  });

  return index.toJSON();
};
