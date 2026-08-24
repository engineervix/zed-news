"use strict";

const globals = require("globals");
const eslintConfigPrettier = require("eslint-config-prettier/flat");

module.exports = [
  {
    ignores: ["public/**", "_references/**"],
  },
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2015,
      },
    },
  },
  eslintConfigPrettier,
];
