# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
