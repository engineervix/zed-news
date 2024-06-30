# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.8.0](https://github.com/engineervix/zed-news/compare/v0.7.0...v0.8.0) (2024-06-30)


### ♻️ Code Refactoring

* back to the way things were before df1e8b1 ([8809a63](https://github.com/engineervix/zed-news/commit/8809a63843e798c8c1cb81fb34ba0933e7e177c5))
* use default repetition penalty ([5cf615f](https://github.com/engineervix/zed-news/commit/5cf615fead209d6fe4a9e3abcfd3804be59f5b24))


### 🚀 Features

* add Times of Zambia ([e5366f9](https://github.com/engineervix/zed-news/commit/e5366f96a4e01768d1005e5dbc60e44d9fd325fd))


### 🐛 Bug Fixes

* new lines ([f18949d](https://github.com/engineervix/zed-news/commit/f18949d5706400b83b6336d2838f9594e1050349))
* remove www from znbc URL ([6d0956b](https://github.com/engineervix/zed-news/commit/6d0956bf4ca42044e84791eb3e7cda50ed28f884))
* rendering of podcast description in template ([bdb12eb](https://github.com/engineervix/zed-news/commit/bdb12eb2ff5c7981f8fbbbd7eee2230649cd8efc))

## [v0.7.0](https://github.com/engineervix/zed-news/compare/v0.6.0...v0.7.0) (2024-03-25)


### ✅ Tests

* fix broken test ([d077ff5](https://github.com/engineervix/zed-news/commit/d077ff5c2cb7b7d625b3244f4982bb65f2886ab1))


### 🚀 Features

* add a better description of each podcast ([fbfe3db](https://github.com/engineervix/zed-news/commit/fbfe3dbeb4131cc3a6269cf05016cf8500d8f100))
* add title and description to the uploaded video ([0e2f6c1](https://github.com/engineervix/zed-news/commit/0e2f6c1c3f2a8c758742eb62480622c3076b832f))
* do not use the same image overlay everytime ([4f66c53](https://github.com/engineervix/zed-news/commit/4f66c53138683359fde634726c67d95587fb6a16))
* make the LLM more creative ([df1e8b1](https://github.com/engineervix/zed-news/commit/df1e8b14b56d6f7c1577c92e9a60352b8a41be2b))


### 🐛 Bug Fixes

* correct broken YAML in episode 196 Nunjucks template ([adf5e93](https://github.com/engineervix/zed-news/commit/adf5e93a1e40b8b9557c28dfc2d06e1a91fe082d))
* description formatting in 2024-03-18.njk ([b03e33f](https://github.com/engineervix/zed-news/commit/b03e33f267642084b10008e3a76c8dd1016d637b))
* ensure we don't have empy description ([c1b40c3](https://github.com/engineervix/zed-news/commit/c1b40c3bb37f342e6510fd7a197da7b3c154701e))
* iensure that the description has no newlines ([438b71c](https://github.com/engineervix/zed-news/commit/438b71cff0220b5f863e9f4014935e9cc960dfe9))
* use the correct path for the images ([f181b20](https://github.com/engineervix/zed-news/commit/f181b206c6286d4fb9f5c4b58c2b9ec07c2a156c))
* yet another description formatting correction ([97150f0](https://github.com/engineervix/zed-news/commit/97150f02ad8f5d21737b026cbec1ffa70cccd314))


### ♻️ Code Refactoring

* minimise social noise ([8dda93e](https://github.com/engineervix/zed-news/commit/8dda93eb381eb8ed0b7f9ed8801a6f47c0b1de93))
* the creativity is too much ([cf4c8b0](https://github.com/engineervix/zed-news/commit/cf4c8b037e8cc565c3a41e85df8a31bcf877ad06))


### ⚙️ Build System

* **deps:** update babel monorepo ([#58](https://github.com/engineervix/zed-news/issues/58)) ([686a762](https://github.com/engineervix/zed-news/commit/686a762f8c56a57fc388fcc17206e1987034cc59))
* **deps:** update dependency beautifulsoup4 to v4.12.3 ([#61](https://github.com/engineervix/zed-news/issues/61)) ([74732fb](https://github.com/engineervix/zed-news/commit/74732fb83a04974cdb65e72cd19d471e58b36902))
* **deps:** update dependency boto3 to v1.34.70 ([#62](https://github.com/engineervix/zed-news/issues/62)) ([033d5c9](https://github.com/engineervix/zed-news/commit/033d5c994deaeb6496c9449920f8faa27d4ea37d))
* **deps:** update dependency core-js to v3.36.1 ([#66](https://github.com/engineervix/zed-news/issues/66)) ([ae04a47](https://github.com/engineervix/zed-news/commit/ae04a47f83572234d29fc7bcec39f20db07644c6))
* **deps:** update dependency css-loader to v6.10.0 ([#67](https://github.com/engineervix/zed-news/issues/67)) ([b51216b](https://github.com/engineervix/zed-news/commit/b51216b3a82bd5777b8f97676eec75137eb4994e))
* **deps:** update dependency jinja2 to v3.1.3 ([#63](https://github.com/engineervix/zed-news/issues/63)) ([2c703de](https://github.com/engineervix/zed-news/commit/2c703dea2989e9a1d434a77731c581941fbe6b03))
* **deps:** update dependency mini-css-extract-plugin to v2.8.1 ([#60](https://github.com/engineervix/zed-news/issues/60)) ([267261e](https://github.com/engineervix/zed-news/commit/267261ec30c245d7cad6b304bbae27ca63bbbaf6))
* **deps:** update dependency together to v0.2.11 ([#64](https://github.com/engineervix/zed-news/issues/64)) ([6bf55dc](https://github.com/engineervix/zed-news/commit/6bf55dca949bdd6dea01e8ff9acdfafdcbd9123d))

## [v0.6.0](https://github.com/engineervix/zed-news/compare/v0.5.0...v0.6.0) (2024-02-14)


### ⚙️ Build System

* **deps:** update dependency black to v23.12.1 ([#59](https://github.com/engineervix/zed-news/issues/59)) ([6643a9a](https://github.com/engineervix/zed-news/commit/6643a9a0fb10de3afb30bb5403d1b9c2edc23fcf))
* **deps:** update dependency boto3 to v1.34.19 ([#54](https://github.com/engineervix/zed-news/issues/54)) ([3138c19](https://github.com/engineervix/zed-news/commit/3138c195e9486bf7a28879459809d7f555061c90))
* **deps:** update dependency cssnano to v6.0.3 ([#51](https://github.com/engineervix/zed-news/issues/51)) ([ee75d90](https://github.com/engineervix/zed-news/commit/ee75d9084d9565a58d8993cf14b7e660287cff68))
* **deps:** update dependency postcss to v8.4.33 ([#52](https://github.com/engineervix/zed-news/issues/52)) ([487d9ad](https://github.com/engineervix/zed-news/commit/487d9ad95c1a4f032d24450022a47278d7c6ee1d))
* **deps:** update dependency sass-loader to v13.3.3 ([#53](https://github.com/engineervix/zed-news/issues/53)) ([c0baa61](https://github.com/engineervix/zed-news/commit/c0baa6155ffc39a43cf68ef5650b9e950ae008e5))
* **deps:** update dependency torch to v2.1.2 ([#55](https://github.com/engineervix/zed-news/issues/55)) ([b31dff3](https://github.com/engineervix/zed-news/commit/b31dff38f42ca55ea84dc93ec7c7487d94523798))
* **deps:** update dependency transformers to v4.36.2 ([#56](https://github.com/engineervix/zed-news/issues/56)) ([2c5d47d](https://github.com/engineervix/zed-news/commit/2c5d47dedc9074b54e5283fe74ccc3ee7bef2f62))
* **deps:** update dependency ua-parser-js to v1.0.37 ([#57](https://github.com/engineervix/zed-news/issues/57)) ([acbbfe8](https://github.com/engineervix/zed-news/commit/acbbfe8c0dddf0d426d6f02a95ea1d2e71e9beb1))


### ♻️ Code Refactoring

* ensure social posts don't start with *Facebook Post:* ([4e5f6a6](https://github.com/engineervix/zed-news/commit/4e5f6a66373c530580ee344d2ff924fa39a641da))
* go back to using mistralai/Mixtral-8x7B-Instruct-v0.1 for social posts ([05cbf07](https://github.com/engineervix/zed-news/commit/05cbf07c52b36db5bc00593cb936acbcbe37ba60))
* simplify social share prompt & switch to Platypus2-70B-instruct ([80ebde2](https://github.com/engineervix/zed-news/commit/80ebde22e6cea1149b22ba73af57029384b3a82f))


### 🐛 Bug Fixes

* add a quick fix to handle connection errors for ZNBC ([710f46c](https://github.com/engineervix/zed-news/commit/710f46c7338dcfb97dbef859d709031301292139))
* address the too many articles problem ([79ee3aa](https://github.com/engineervix/zed-news/commit/79ee3aac8358666fdfe8c7311a9b18602ac87cdd))
* correct the buggy fix in 710f46c ([64be24d](https://github.com/engineervix/zed-news/commit/64be24d7e63275c0d1c00434dd31e1363a480035))
* remove baclticks in social post and correct conditional statements ([b078422](https://github.com/engineervix/zed-news/commit/b07842220855c17686b2f429dd25b5cff121c661))
* simplify pagination ([56b1217](https://github.com/engineervix/zed-news/commit/56b1217bcf8900d71efdddc6d3065347a6cf4414))
* use the correct font and adjust text duration ([e22ca82](https://github.com/engineervix/zed-news/commit/e22ca82947e6b57977efe3182376d0eb31837124))


### 🚀 Features

* create facebook post accompanied by video ([f7a7a73](https://github.com/engineervix/zed-news/commit/f7a7a7334bc3256518524c9cbf428f9e5cff51f0))
* create video and post to facebook ([f5c807f](https://github.com/engineervix/zed-news/commit/f5c807f2b40edd5841e4e67b009badae04e4d791))
* use openchat/openchat-3.5-1210 for social posts ([3bea658](https://github.com/engineervix/zed-news/commit/3bea6583bf330a13374e5d53ad7ab6df9fe8c4b8))
* use Qwen/Qwen1.5-14B-Chat for the transcript ([b43e5f7](https://github.com/engineervix/zed-news/commit/b43e5f74c1734a257e92c4b376b35c0cc640b016))
* use the `NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT` model ([1d6ffdb](https://github.com/engineervix/zed-news/commit/1d6ffdbc6dfd3ae4090d5c3efd8bddd58963b584))

## [v0.5.0](https://github.com/engineervix/zed-news/compare/v0.4.0...v0.5.0) (2024-01-02)


### ✅ Tests

* mock together summarisation backend ([ca7b9ac](https://github.com/engineervix/zed-news/commit/ca7b9ac1f5bc1b754eee792253bbf10102abd85e))
* temporarily remove failing test and exercise caution with bs4 ([f76b321](https://github.com/engineervix/zed-news/commit/f76b321b0efdd4b481752fe4b0cfc60b0a658ec2))


### 🚀 Features

* install replicate ([40c12ba](https://github.com/engineervix/zed-news/commit/40c12bad73bd363fd7165c955678e0af761c00d9))
* let the LLM actually present the podcast ([d0e63b3](https://github.com/engineervix/zed-news/commit/d0e63b3e188a74ec1b4b4af550fcb638bab0887b))
* use together.ai & bump langchain to 0.0.348 ([63e68e7](https://github.com/engineervix/zed-news/commit/63e68e738f852025f7b0f1fcde812630be65926e))
* use vicuna-13b-v1.5-16k and garage-bAInd/Platypus2-70B-instruct ([16e2877](https://github.com/engineervix/zed-news/commit/16e28772a8e82e6e5fcd25d5faad476f738873a4))


### ♻️ Code Refactoring

* change prompt and do not use one-sentence summary ([5b0ad43](https://github.com/engineervix/zed-news/commit/5b0ad43fbb0b0d378cb0e0adca49471e4ade7c75))
* tweak the content generation ([c1b6237](https://github.com/engineervix/zed-news/commit/c1b62372b4b218f01146b912ddc1d45642ea472c))
* tweak the together.ai invocation ([39199f1](https://github.com/engineervix/zed-news/commit/39199f1e14999fe5a1ddcb8d74350d36bc4897db))
* update codebase to incorporate new ORM ([8d2fa06](https://github.com/engineervix/zed-news/commit/8d2fa06b05899113050a1b03875ad23be1653750))
* yet another small tweak ([b81538c](https://github.com/engineervix/zed-news/commit/b81538c89227be304891cff832b10c3a1bf137d2))


### 👷 CI/CD

* **deps:** update sosedoff/pgweb docker tag to v0.14.2 ([daf654d](https://github.com/engineervix/zed-news/commit/daf654df8676cdff6692eae85c3ea1628faaf579))


### 🐛 Bug Fixes

* **deps:** update dependency num2words to v0.5.13 ([#50](https://github.com/engineervix/zed-news/issues/50)) ([d9c1593](https://github.com/engineervix/zed-news/commit/d9c15936a50450063554fd94d540fd6b4ee7bbc2))
* ensure that import_db_dump task works correctly ([c13067f](https://github.com/engineervix/zed-news/commit/c13067f70629e378186e9c544d4834211a04a056))
* erroneous transcript generation ([0fdb6c9](https://github.com/engineervix/zed-news/commit/0fdb6c9f9f6addf4fb5383173cca26e5e5e63a54))


### ⚙️ Build System

* **deps:** update dependency babel-loader to v9.1.3 ([#43](https://github.com/engineervix/zed-news/issues/43)) ([fd4f110](https://github.com/engineervix/zed-news/commit/fd4f110f8bf70ce1b28a267e570fb60a1c7b2dc7))
* **deps:** update dependency bootstrap to v5.3.2 ([#47](https://github.com/engineervix/zed-news/issues/47)) ([df4d544](https://github.com/engineervix/zed-news/commit/df4d5444cb85baac75a7d4d0fa38dc1512d785d0))
* **deps:** update dependency boto3 to v1.34.11 ([#32](https://github.com/engineervix/zed-news/issues/32)) ([43b6536](https://github.com/engineervix/zed-news/commit/43b653636b7fe7053da2cab6fa36e6f4e74f413b))
* **deps:** update dependency cssnano to v6.0.2 ([#44](https://github.com/engineervix/zed-news/issues/44)) ([d2601cf](https://github.com/engineervix/zed-news/commit/d2601cfeff58cfbbd73cd075fa864f54aab4251c))
* **deps:** update dependency feedparser to v6.0.11 ([#48](https://github.com/engineervix/zed-news/issues/48)) ([539cfe6](https://github.com/engineervix/zed-news/commit/539cfe60b1cc2de9b7e282a3033de1365a001c98))
* **deps:** update dependency langchain to ^0.0.353 ([#49](https://github.com/engineervix/zed-news/issues/49)) ([7a9987b](https://github.com/engineervix/zed-news/commit/7a9987b6cdabaec558405d38ccffaf6bf09c5677))
* **deps:** update dependency rimraf to v5.0.5 ([#45](https://github.com/engineervix/zed-news/issues/45)) ([ee33868](https://github.com/engineervix/zed-news/commit/ee33868d367a1d08d4cd3a92c39d2f930338aa72))
* replace tortoise-orm with peewee. No more async ([af02a49](https://github.com/engineervix/zed-news/commit/af02a498a09ec7104c379d118a6dbedb2bf1923d))

## [v0.4.0](https://github.com/engineervix/zed-news/compare/v0.3.2...v0.4.0) (2023-11-22)


### 👷 CI/CD

* bump Node from v16 to v18 ([2c2b83e](https://github.com/engineervix/zed-news/commit/2c2b83e23d5f0379483ce84d5133f23451e97497))
* remove requirements.txt because cloudflare recognizes poetry ([c899203](https://github.com/engineervix/zed-news/commit/c899203ac088f1a79cf52c09ddc13fd3edee52ec))


### 🚀 Features

* programmatically post to facebook ([52567c7](https://github.com/engineervix/zed-news/commit/52567c764bd7ae05dcd4a91788f7cc0bc8afbbfc))


### 🐛 Bug Fixes

* ensure that file is closed ([7837abd](https://github.com/engineervix/zed-news/commit/7837abda79aa69d5ff6d21ed3211efd325fc1639))


### ⚙️ Build System

* **deps:** add html5lib ([54c6b3c](https://github.com/engineervix/zed-news/commit/54c6b3c6556b7898c1ed8893284c5065aced81e7))
* **deps:** fix psycopg dependencies to allow for better multiarch compatibility ([f38ab3f](https://github.com/engineervix/zed-news/commit/f38ab3f0a1dcfb43cebd547834b61d752eed4238))
* switch to node v18 ([27a0249](https://github.com/engineervix/zed-news/commit/27a02499e848332984447e44727f9493cbf41d41))
* update poetry to 1.6.1 ([53d0ade](https://github.com/engineervix/zed-news/commit/53d0ade3a125eb51fe7bbe458340169598e69cee))


### ♻️ Code Refactoring

* account for the situation where `docker-compose` doesn't exist ([0712568](https://github.com/engineervix/zed-news/commit/07125680ecc711b9f4bfed71b2095b8502fe904f))
* change social post prompt ([1ff1aca](https://github.com/engineervix/zed-news/commit/1ff1acaee9507cb68358b60484196178fef126e4))
* update Daily Mail article detail parser ([33e330e](https://github.com/engineervix/zed-news/commit/33e330efe50f6bbe1372f05198a7136f97de4a7e))
* use html5lib instead of html.parser ([50c2dfa](https://github.com/engineervix/zed-news/commit/50c2dfa65db0e79b6733ecadad05e3a940b79097))

## [v0.3.2](https://github.com/engineervix/zed-news/compare/v0.3.1...v0.3.2) (2023-10-15)


### 🐛 Bug Fixes

* handle a situation where article div doesn't have expected class ([8894eae](https://github.com/engineervix/zed-news/commit/8894eaebdb83305b9a22edfe0f67630653c7869d))


### 📝 Docs

* minor documentation fixes ([f58fd30](https://github.com/engineervix/zed-news/commit/f58fd30f7c569113748cd654fd5f6ac81920d3c9))


### ⚙️ Build System

* **deps:** run `poetry lock --no-update` ([0b16b3d](https://github.com/engineervix/zed-news/commit/0b16b3d4fd8e9ed2d15d3effc90f667a409682da))
* **deps:** update dependency langchain to v0.0.239 ([#33](https://github.com/engineervix/zed-news/issues/33)) ([7f21573](https://github.com/engineervix/zed-news/commit/7f2157332534b8105de47dc0218d5cfc6e207c15))
* **deps:** update dependency ruff to v0.0.291 ([#24](https://github.com/engineervix/zed-news/issues/24)) ([1afb09f](https://github.com/engineervix/zed-news/commit/1afb09fc55812897aec0e64dcd922a434d34992d))
* **deps:** update node.js to v16.20.2 ([#30](https://github.com/engineervix/zed-news/issues/30)) ([809af83](https://github.com/engineervix/zed-news/commit/809af836f0efb9382db5786e0ba730f864344b71))

## [v0.3.1](https://github.com/engineervix/zed-news/compare/v0.3.0...v0.3.1) (2023-07-16)


### 👷 CI/CD

* **deps:** update sosedoff/pgweb docker tag to v0.14.1 ([1f5bd91](https://github.com/engineervix/zed-news/commit/1f5bd911cfe2a84087dc92aa59e915712696c434))


### 🐛 Bug Fixes

* quick and dirty fix for exceeding token limit ([94754b8](https://github.com/engineervix/zed-news/commit/94754b87479771d652acde136e00988ba3673018))
* yet another hack to manage max token limit ([28008a1](https://github.com/engineervix/zed-news/commit/28008a15b189f04f326cdd53a9041ec3d09f72cc))

## [v0.3.0](https://github.com/engineervix/zed-news/compare/v0.2.0...v0.3.0) (2023-06-24)


### 💄 Styling

* let's use animate on scroll ([494249d](https://github.com/engineervix/zed-news/commit/494249dbd59f2698987ef48cff592641df4aec51))


### 👷 CI/CD

* add environment variables for CI tests ([00abab0](https://github.com/engineervix/zed-news/commit/00abab019a79dacc71a81c6dcfb1b678a4d7c4d7))
* fix placement of env variables ([6934d72](https://github.com/engineervix/zed-news/commit/6934d72ef3a1a750ec4d4ac9b523b5ad6e6ebcd0))
* fix poetry setup ([cdc7fb5](https://github.com/engineervix/zed-news/commit/cdc7fb509dee22129d5424b1254957debe231961))
* install poetry ([bb0e2ba](https://github.com/engineervix/zed-news/commit/bb0e2ba818c928bad487c23a1ad7110740e05e50))
* use latest version of `actions/checkout` ([d5aa008](https://github.com/engineervix/zed-news/commit/d5aa00881267ac56a9cdba60dcd12c9ceb9d1bd2))


### ⚙️ Build System

* **deps-dev:** update dependency sass-loader to v13.3.2 ([#25](https://github.com/engineervix/zed-news/issues/25)) ([d160a24](https://github.com/engineervix/zed-news/commit/d160a24f708ffc9844e4a7016e16348c3fa05520))
* **deps:** bump outdated python packages ([79559cc](https://github.com/engineervix/zed-news/commit/79559ccb18a12efeb21cede31e53664c6be36d9c))
* **deps:** remove animate.css ([a042cce](https://github.com/engineervix/zed-news/commit/a042ccee5bda61ab9f325952d92ec25bff87b8d2))
* **deps:** update dependency webpack-cli to v5.1.4 ([#26](https://github.com/engineervix/zed-news/issues/26)) ([9d32366](https://github.com/engineervix/zed-news/commit/9d323661bb2b797f11aeefe3c81aaf808d5f6395))
* install mutagen ([e83f772](https://github.com/engineervix/zed-news/commit/e83f7720c37c9efb6d0554181ccf0bf0d826ee26))
* install poetry and remove extraneous config files ([b4ab738](https://github.com/engineervix/zed-news/commit/b4ab7380d07d561fb2b2b7e470040278b67e68a4))
* replace isort and flake8 with ruff ([31280f7](https://github.com/engineervix/zed-news/commit/31280f79379baff98b7f775c63656d559cb3fb4b))
* temporarily add requirements.txt to fix CF builds ([80799c9](https://github.com/engineervix/zed-news/commit/80799c944a40f6cb184c090eb34f40a2f4c4b481))


### ✅ Tests

* add some sample test data to work with ([8619606](https://github.com/engineervix/zed-news/commit/8619606b277b1767b3cbcc746b003dfd03756d81))
* add test for `random_opening()` ([ee21e4c](https://github.com/engineervix/zed-news/commit/ee21e4c561b9801eec68df169267fcee6aa34e66))
* fix coverage configuration ([b06218d](https://github.com/engineervix/zed-news/commit/b06218d1ddc5eff5faf8648278cb1cc446337a9a))
* fix test_update_article_with_summary_article_not_found ([3c700b3](https://github.com/engineervix/zed-news/commit/3c700b343d604af803adaa31e5040162b28d4677))
* test transcript creation ([a502554](https://github.com/engineervix/zed-news/commit/a50255433f595fe16eb212a38ca59b3ca614f98d))
* write more tests ([a5aed89](https://github.com/engineervix/zed-news/commit/a5aed89ecb13fee3801b9cccc92a82e82f83a988))


### 🐛 Bug Fixes

* avoid returning multiple Article objects ([26b60ea](https://github.com/engineervix/zed-news/commit/26b60eac86ce267cee6cf5c6b597d9f19b045299))
* correct metadata for episode 004 ([af6dac4](https://github.com/engineervix/zed-news/commit/af6dac44396a0c3abd4e078050111064dd425890))
* datetime.datetime is the one with `strptime` method ([f88063b](https://github.com/engineervix/zed-news/commit/f88063b5527eb31318ccd32484165c7b01b7b3dc))
* play/pause button controls & state on home page ([8ca6d02](https://github.com/engineervix/zed-news/commit/8ca6d025de6a4f81a8f2b4a69cf74887c4f57a04))
* specify the correct(ish) episode pubDate ([491248c](https://github.com/engineervix/zed-news/commit/491248c3a2bdfe2572ced4d5ff5fad8eae93c060))
* use mutagen to determine mp3 length ([6ce9f19](https://github.com/engineervix/zed-news/commit/6ce9f19423ccd2e1fee1e0ae7030b337bec57c54))
* use the correct syntax for rich text in episode description ([4079a66](https://github.com/engineervix/zed-news/commit/4079a66b1bd681b0ba022043b63d393c2e5793b3))


### ♻️ Code Refactoring

* reduce the treble gain by half (from 6dB to 3dB) ([c3c0f61](https://github.com/engineervix/zed-news/commit/c3c0f61ff48553f943f5d23229ae95de91226101))
* remove spacing on google/apple podcast button, and ad URLs ([47e741d](https://github.com/engineervix/zed-news/commit/47e741d2511fe39da0a97e4ee2ee0762d9ac41a4))
* use description instead of just specifying episode No. ([cd04555](https://github.com/engineervix/zed-news/commit/cd0455564c4cc1cd870df4c0ff8b0856226f9f65))


### 🚀 Features

* add **More ways to listen** button and modal ([239d429](https://github.com/engineervix/zed-news/commit/239d429db99afab1afeebf58dc3b3ac61245aea5))
* change the voice sampling rate to 44.1kHz ([110bd71](https://github.com/engineervix/zed-news/commit/110bd71b03dccecc54ec11b9d2d92f3f9cf0e9b9))
* conditional rendering of (social) icons in footer ([38fcbdc](https://github.com/engineervix/zed-news/commit/38fcbdcd8436e4b4247358a1a26f9c043d1ff51e))
* separate modules for summarization backends ([92c9af0](https://github.com/engineervix/zed-news/commit/92c9af085a8ab4a0398b31ad6d8a4a547980c576))

## [v0.2.0](https://github.com/engineervix/zed-news/compare/v0.1.0...v0.2.0) (2023-06-05)


### 🐛 Bug Fixes

* argument passed to random.choice for many articles ([1720456](https://github.com/engineervix/zed-news/commit/1720456f9108979b6a48a391086d9a592dcf922d))
* reduce treble gain from 10dB to 6dB ([bc031f9](https://github.com/engineervix/zed-news/commit/bc031f97b3bb179e067f0f39086a5699b1eb920f))
* timeago implementation ([a11d699](https://github.com/engineervix/zed-news/commit/a11d6995381100c1ff165a9cd6f351232a06c8e8))
* whitespace breaking accordion classes ([2f48a5f](https://github.com/engineervix/zed-news/commit/2f48a5f05dadb68b83708d9e5e6cde2ca368d235))


### 💄 Styling

* fix broken stylelint config ([4549c38](https://github.com/engineervix/zed-news/commit/4549c3877e2c6267b6d839d5490108602aba9920))
* fix stylelint ([73ccc23](https://github.com/engineervix/zed-news/commit/73ccc23115fbda455ea845c86f6ae9c11e999ece))


### 🚀 Features

* add RSS feed ([26389ca](https://github.com/engineervix/zed-news/commit/26389cad404512c3a6998b9bcda60d01e53374f3))
* add social sharing buttons and fix some minor bugs ([1b5cf8a](https://github.com/engineervix/zed-news/commit/1b5cf8a83ddc07eb4f3bfbb2d0f076c15ab5bdae))
* setup and configure 11ty web project ([813e904](https://github.com/engineervix/zed-news/commit/813e904b86d58b5aced7f8641748b1f76d6d29c4))
* sound equalisation and album art for the audio file ([8f41036](https://github.com/engineervix/zed-news/commit/8f4103644946ed2fbf0dc275cbc7fc36367e1ca7))
* use aerich for database migrations ([0306101](https://github.com/engineervix/zed-news/commit/030610186f852a95c3d4d42a566f467b885a4135))
* use apprise to send telegram notifications ([fb2b123](https://github.com/engineervix/zed-news/commit/fb2b123a9d8d4b6ef2540553d5d799d8b25f0871))
* use bootstrap 5.3, with built-in dark mode support ([41c1181](https://github.com/engineervix/zed-news/commit/41c118122760570e297b39db9b836ced0657df91))
* use Jinja2 to render njk template for 11ty ([d65e632](https://github.com/engineervix/zed-news/commit/d65e632d79bb27b24906fd6ac36834adc8605770))


### ✅ Tests

* write some tests ([b50f5d8](https://github.com/engineervix/zed-news/commit/b50f5d83fe34128b85aea184c160c113542a1c48))


### 👷 CI/CD

* add cache-dependency-path on setup-python action ([edba603](https://github.com/engineervix/zed-news/commit/edba60301fa8558cb661f5d7d539d867e87037fd))
* add Github Actions config ([3a08a93](https://github.com/engineervix/zed-news/commit/3a08a93bab623c5bf3d4c9c4beaf34e196519c9a))
* add test suite to CI/CD ([1178143](https://github.com/engineervix/zed-news/commit/1178143a7a3bf45ca40c473e1d1887c4a00181fb))
* fix coverage data upload ([0877142](https://github.com/engineervix/zed-news/commit/0877142295a455d54933fda2f039f64ca3b4031e))
* fix extraction of total coverage ([312630f](https://github.com/engineervix/zed-news/commit/312630fb72943309e306a8c4b136073081563c2b))
* fix python version ([3acef2d](https://github.com/engineervix/zed-news/commit/3acef2daf6c6510a870f4342a637d1a030269b11))
* fix test job configuration ([75c62d0](https://github.com/engineervix/zed-news/commit/75c62d00c41d310b4dc632f1bab8faa4b3690c28))
* fix timezone setup in test job ([1afd4be](https://github.com/engineervix/zed-news/commit/1afd4be814a3456c7f04eeb7f5ac605e542e5b2f))
* generate coverage badge ([a54be8f](https://github.com/engineervix/zed-news/commit/a54be8fefa5e663cb8f87ea19bf3826abfc99858))
* install things as root ([d95dc8e](https://github.com/engineervix/zed-news/commit/d95dc8e8920dd4a9e334bfed5a2a6e34db50fb53))
* no need to install unnecessary stuff ([c561911](https://github.com/engineervix/zed-news/commit/c5619114e32e1f3e965f01341ea2b7386454481e))
* remove packages already installed ([8b21a11](https://github.com/engineervix/zed-news/commit/8b21a11a27e729db9d595ef8a57d033da8eaa4f9))
* run prettier ([1116575](https://github.com/engineervix/zed-news/commit/11165759348cb52cdfcb2155e51ae4611d808f53))
* run shellcheck on shell script(s) ([58b2291](https://github.com/engineervix/zed-news/commit/58b2291ff691cd8b66be883ea369308494c72353))


### ⚙️ Build System

* add .nvmrc with node version set to 16 ([cf208ac](https://github.com/engineervix/zed-news/commit/cf208ac81c6a0d22ac0c7cf8ff29403cb766a420))
* add a bash script to be run by cron ([901ca45](https://github.com/engineervix/zed-news/commit/901ca45e3e71c81b7caf6c8c9cdd4c4b85f0a581))
* **deps:** add tortoise-orm and related packages ([97ff236](https://github.com/engineervix/zed-news/commit/97ff236b7ae12eddd2b9e8e5ecfc0a6703ba3d25))
* **deps:** fix dependency conflicts & CI dependency installation ([c16ad40](https://github.com/engineervix/zed-news/commit/c16ad4028bad4b2caec60724807e6f1120368bde))
* **deps:** install timeago.js ([7c61700](https://github.com/engineervix/zed-news/commit/7c617009469d9c58cdc59cfc23a52239fab50ff9))
* **deps:** update dependency boto3 to v1.26.146 ([#2](https://github.com/engineervix/zed-news/issues/2)) ([adf0aa9](https://github.com/engineervix/zed-news/commit/adf0aa9cf3eb56c86e16fd605b01e7a0e32fbb72))
* **deps:** update dependency botocore to v1.29.146 ([#3](https://github.com/engineervix/zed-news/issues/3)) ([fb4bb7e](https://github.com/engineervix/zed-news/commit/fb4bb7e17f84cbf7fde64740c96095c9eecc4520))
* **deps:** update dependency langchain to v0.0.189 ([#5](https://github.com/engineervix/zed-news/issues/5)) ([1b3108b](https://github.com/engineervix/zed-news/commit/1b3108b075457cdb12ee9944871c0a474f274b39))
* **deps:** update dependency typing-extensions to v4.6.3 ([#7](https://github.com/engineervix/zed-news/issues/7)) ([b916b65](https://github.com/engineervix/zed-news/commit/b916b6580d415848a4e94ee49348b11f88ed4de2))
* **deps:** update python dependencies ([05f6f24](https://github.com/engineervix/zed-news/commit/05f6f24f43251c2813cd8af158da525b08ea02b8))
* **deps:** use psycopg2-binary due to failing cloudflare pages build ([b5c4b34](https://github.com/engineervix/zed-news/commit/b5c4b34eb3684394c04d1720d04323e416efeb4a))
* images must be built in case there are significant changes ([834636d](https://github.com/engineervix/zed-news/commit/834636d938060363688788a82524203c8f0d2f95))
* integrate healthchecks.io into the cron job ([a69733e](https://github.com/engineervix/zed-news/commit/a69733e1f47ad9b1dbf03dc8196d9e3164bdd593))
* specify python version to fix cloudflare pages build failure ([f595b61](https://github.com/engineervix/zed-news/commit/f595b612bedf2e13a476c39dc4f04a65b3f02659))
* switch to ubuntu as base image ([d07dd37](https://github.com/engineervix/zed-news/commit/d07dd370a454da3ef76e45dd9f077c2cf6c353a4))
* update Dockerfile ([773694c](https://github.com/engineervix/zed-news/commit/773694c4821d3c8d1f664f83bb50e7a913014f0d))
* update ENV variables ([3af2369](https://github.com/engineervix/zed-news/commit/3af2369117be0dc4df420aae06e19cfcf58574b9))
* use docker for python developement ([4cb7e4e](https://github.com/engineervix/zed-news/commit/4cb7e4eed7a32d04f6b0299446ddda702887172d))


### ♻️ Code Refactoring

* add aerich-related tasks and update paths ([7764f68](https://github.com/engineervix/zed-news/commit/7764f687961e6e2b0da04abe5d0534b9fd52d701))
* add album art and reorganize images ([abb52ab](https://github.com/engineervix/zed-news/commit/abb52abb1fe6d7054267e6f54d1b699705a33b13))
* add correct button depending on OS ([2efdf69](https://github.com/engineervix/zed-news/commit/2efdf69c0ec32ec9f3423f939abf4be731bd7bd9))
* add facebook icon and update dev link ([2b18128](https://github.com/engineervix/zed-news/commit/2b181282086c31500b210d91187edc6c0aa33b81))
* change code organisation ([ad73f5b](https://github.com/engineervix/zed-news/commit/ad73f5bb85d784ad3f572fdf4db325d246cb3869))
* finalise toolchain for the podcast audio production ([9e08ebd](https://github.com/engineervix/zed-news/commit/9e08ebd57b2f18a962fd100114a573d1eab6a3b6))
* improve a number of litle things ([a69ea21](https://github.com/engineervix/zed-news/commit/a69ea21bf4087dcb8fba615ec8c218f2e8f2e606))
* improve code structure and some some abstractions ([5102f9d](https://github.com/engineervix/zed-news/commit/5102f9da8fb5059e41e6dd64d098876938b0399e))
* improve RSS feed data ([f65d189](https://github.com/engineervix/zed-news/commit/f65d189dd01837faa2e8e1ee693d1702d14a6eae))
* randomize some phrases ([901b7f1](https://github.com/engineervix/zed-news/commit/901b7f17e29a30adadf57686be4a2462047f22c4))
* regenerate aerich database migrations ([f2f1554](https://github.com/engineervix/zed-news/commit/f2f15549e298a3337129758a0977715ee59b948d))
* remove external playing for now. ([fc4aa3d](https://github.com/engineervix/zed-news/commit/fc4aa3df8f0d6f7b43f19ae1e46dbe578d6bff56))
* update 11ty config to include RSS filter ([018f1ea](https://github.com/engineervix/zed-news/commit/018f1ea90bdaec0175f236aa0f4bf274e04c37d4))
* update default date in models ([e45ca83](https://github.com/engineervix/zed-news/commit/e45ca830e5393999d70a88b1ce3b9b6536ee2b9a))
* update paths from src/... to app/... ([174720a](https://github.com/engineervix/zed-news/commit/174720a0163f8d9e305ec93a58d77940fe81df8c))
* update templates ([3518d71](https://github.com/engineervix/zed-news/commit/3518d71b2cf4bcf4775e65b89019f5cbcb1b3eee))


### 📝 Docs

* add badges and TOC ([78a7679](https://github.com/engineervix/zed-news/commit/78a7679f914ce277cbbb53c5db85d51d62c106c7))
* add some documentation and contribution guidelines ([d713afa](https://github.com/engineervix/zed-news/commit/d713afa905bcc1f27f8da77b9039652408bf4725))
* update the docs by adding deployment guide ([f468bec](https://github.com/engineervix/zed-news/commit/f468becc7ae0b9b13d1ec7e6098f28c94ed76e1e))

## [v0.1.0](https://github.com/engineervix/zed-news/compare/v0.0.0...v0.1.0) (2023-05-26)


### 🐛 Bug Fixes

* use correct filepaths and squash a few other bugs ([608c884](https://github.com/engineervix/zed-news/commit/608c8842546b11c419ea69d72b602761a8c6345c))
* use correct path to content file, and decorate the toolchain fn with `@task` ([2cc5ab1](https://github.com/engineervix/zed-news/commit/2cc5ab1c6302475cc654d80b17ef2d5df5e7f91a))


### 🚀 Features

* add script to fetch today's latest news from ZNBC ([d25b56c](https://github.com/engineervix/zed-news/commit/d25b56cabca87a16b6aee0de1ddb8b018869c31f))
* automate everything, no more manual processes ([3b13230](https://github.com/engineervix/zed-news/commit/3b13230d0a7332c51eade5a30b0663629b44d0ce))
* play the audio file using VLC ([68e119b](https://github.com/engineervix/zed-news/commit/68e119b34c625b43d27ae975fc0f9be66f475dea))
* use boto3 SDK ([5071ea0](https://github.com/engineervix/zed-news/commit/5071ea0d9a0a1c594293a1e2ffa804652a0be781))
* use Invoke for task automation ([257be9e](https://github.com/engineervix/zed-news/commit/257be9e4b4ab6aec0b2c3df63b7c573e51cd5719))


### ♻️ Code Refactoring

* add more invoke tasks ([43383ac](https://github.com/engineervix/zed-news/commit/43383acff7a883a2b970ff041c5ef8d8df7fbf48))
* Ayanda is a much better host than Emma ([1ee7b21](https://github.com/engineervix/zed-news/commit/1ee7b2167fa67191e2b26384219eca74dd8157f3))
* modify for use in epison 002 ([6190d33](https://github.com/engineervix/zed-news/commit/6190d33852c478adc23df6b619b9806f64a40497))
* modify for use in epison 003 ([4c24170](https://github.com/engineervix/zed-news/commit/4c24170c84f73793d1b98f5b73392ba4143b60fe))
* reorganize project files ([52e1340](https://github.com/engineervix/zed-news/commit/52e134002607e798f1f364d22433e72ebde3d170))
* reorganize project files. This should have been part of 52e1340 ([530dce5](https://github.com/engineervix/zed-news/commit/530dce55c4860839cd766bbd1781404a208b144f))
* use UA on requests job ([1423323](https://github.com/engineervix/zed-news/commit/1423323290552acc735a1625c6b272619586e8de))


### 📝 Docs

* add more TODOs ([e27d882](https://github.com/engineervix/zed-news/commit/e27d882163607e2c4882e837b1886d994f915fbf))
* add notes ([574d575](https://github.com/engineervix/zed-news/commit/574d575a3e1d7f7d78e3222835470e2481911750))
* add README ([bbeec27](https://github.com/engineervix/zed-news/commit/bbeec273e64be98c854e972f47fad0a0f16f3bc4))
* add TODO items ([64afb3c](https://github.com/engineervix/zed-news/commit/64afb3cb8fed7a67b23042da004fbf871b6e34b3))
* update description in README ([9c7ce19](https://github.com/engineervix/zed-news/commit/9c7ce19a311ed6cd7cbc324f91d0ec62622232c5))
* yet another TODO ([a6ce3a4](https://github.com/engineervix/zed-news/commit/a6ce3a4223d0be45c106b569b3cf98583e3eaf87))


### ⚙️ Build System

* **deps:** add more dependencies ([0a11aa6](https://github.com/engineervix/zed-news/commit/0a11aa67211ea03754d4e784aaeb3d3528d03279))
* **deps:** install eyed3 and tiktoken ([a7899a2](https://github.com/engineervix/zed-news/commit/a7899a26d7c03750b923a2fc4dd234d6481ae2d5))
* **deps:** use pyproject.toml to manage dependencies ([3c98916](https://github.com/engineervix/zed-news/commit/3c989160d937cf459b12f033c136900f34c006b7))
* install commitizen ([3db6785](https://github.com/engineervix/zed-news/commit/3db678552f4373d9ae04af6e5a0ecbaa267b0174))
* use Node.js ([88c7c82](https://github.com/engineervix/zed-news/commit/88c7c8258d8684b38d91696fddfc7ab98510560f))
