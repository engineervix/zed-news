# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0.0](https://github.com/engineervix/zed-news/compare/v0.10.0...v1.0.0) (2025-06-13)


### ⚠ BREAKING CHANGES

* The project has transitioned from generating
audio podcast episodes to text-based news digests.
This represents a fundamental change in the project's
content format, delivery method and project architecture.

### 🚀 Features

* foundational work for transitioning from audio podcast to news digest ([388801e](https://github.com/engineervix/zed-news/commit/388801e08e456e2a3fccaa451745b3b0714bedd8))
* news digests ([c854131](https://github.com/engineervix/zed-news/commit/c8541311768bcae11a1a66e3921c1c64d74fa1f4))
* remove AWS Polly TTS voice processing component ([ca0d94f](https://github.com/engineervix/zed-news/commit/ca0d94f8d98c888646bb66a36a2d4b38999261f9))
* remove FFmpeg audio mixing and S3 upload functionality ([e97ed38](https://github.com/engineervix/zed-news/commit/e97ed3865853da88c35029e15491c3043cb4b3b6))
* remove podcast transcript generation component ([75bb81c](https://github.com/engineervix/zed-news/commit/75bb81cc357a39f269676403a663a56083ad6340))
* transition from podcast episodes to news digests ([ca30261](https://github.com/engineervix/zed-news/commit/ca30261ff1ad4749c7c0d7d3f3f313f3b6ad8cc0))


### 🐛 Bug Fixes

* **deps:** update dependency @fortawesome/fontawesome-free to v6.7.2 ([#165](https://github.com/engineervix/zed-news/issues/165)) ([d20d21b](https://github.com/engineervix/zed-news/commit/d20d21bc44a087c2b28af898d6dd1a5ac9b1bc15))
* **deps:** update dependency boto3 to v1.38.28 ([#157](https://github.com/engineervix/zed-news/issues/157)) ([1d66fb1](https://github.com/engineervix/zed-news/commit/1d66fb126b8d89ae23d6fa75956369622058a6c8))
* **deps:** update dependency bpython to v0.25 ([#166](https://github.com/engineervix/zed-news/issues/166)) ([f87622a](https://github.com/engineervix/zed-news/commit/f87622a122d90a546fa04e1643c90b6d5b1ec855))
* **deps:** update dependency langchain-openai to v0.3.19 ([#158](https://github.com/engineervix/zed-news/issues/158)) ([7fc0ecc](https://github.com/engineervix/zed-news/commit/7fc0eccf0f7b5fff6dfa15d9db60d5f4a9fdd143))
* lazily initialise GEMINI client, nunjucks template generation ([ab4f482](https://github.com/engineervix/zed-news/commit/ab4f48215c2c1e774ac3feeff45148d4933e38ab))
* prevent duplicates, remove unnecessary information ([bb2b019](https://github.com/engineervix/zed-news/commit/bb2b01986efd1eb572e58c985bd6261df44e78d5))
* template rendering and styling ([c42c006](https://github.com/engineervix/zed-news/commit/c42c0069c066992726b06dab699007e9ccdd7dbe))
* **testing:** Correct file path generation in tests ([ab0273a](https://github.com/engineervix/zed-news/commit/ab0273a81437ecb0c9170d19964ce1f4aa17620b))
* use correct model ([b36fc62](https://github.com/engineervix/zed-news/commit/b36fc6259d49229545b74e9071d3ca0f5a0ef48a))


### 📝 Docs

* update README ([46562fe](https://github.com/engineervix/zed-news/commit/46562fee643c066f5ebc72a4a997866cdde05ab3))


### 💄 Styling

* improve ui on homepage and remove un-necessary items ([a9375df](https://github.com/engineervix/zed-news/commit/a9375df5a83be0ea26cf5dd4d7fb50fc9b57fe39))
* make stylelint happy ([a3e2497](https://github.com/engineervix/zed-news/commit/a3e2497dd6bd6225cee58ed94f15aa2ba2878f0d))
* ui enhancements on news listing template ([1cb7f8a](https://github.com/engineervix/zed-news/commit/1cb7f8a707a21afab7571959731b22d1b09c6746))
* ui/ux enhancements on single news item, plus share functionality ([6bc8504](https://github.com/engineervix/zed-news/commit/6bc85047201ea03ce56cfa7880c7ad8d300dcbcc))
* update assets ([2eb9331](https://github.com/engineervix/zed-news/commit/2eb9331852c047a7c727926f598bd9a554dc2cff))
* update logo ([9ec5c89](https://github.com/engineervix/zed-news/commit/9ec5c89856aaea04cafe55718c1b4d48ef734f02))


### ♻️ Code Refactoring

* **.eleventy.js:** news collection and custom date filters ([06d4e43](https://github.com/engineervix/zed-news/commit/06d4e430c01b7b7834119738d416daf5d4f196ff))
* content changes on home page ([2ffb5d3](https://github.com/engineervix/zed-news/commit/2ffb5d3c55b373c910e866909093a3eb720d861a))
* remove lots of unused stuff, cleanup and fix tests ([ecbd9a2](https://github.com/engineervix/zed-news/commit/ecbd9a2b7924bdb61a494db2f75a539fd0da730b))
* rename .env.sample -> .env.example ([a539c6c](https://github.com/engineervix/zed-news/commit/a539c6c511b005b89baa9d4c846ac04e02fa0817))
* reorganise code and remove things we don't need ([d678b0a](https://github.com/engineervix/zed-news/commit/d678b0a982befa925365a603532e466b9bd659c0))
* replace tomli with built-in tomllib ([ac6e716](https://github.com/engineervix/zed-news/commit/ac6e716efe4faaeb20df558026048ef942d616d7))
* update content on about page, and fix apple button ([8080000](https://github.com/engineervix/zed-news/commit/80800004e4b8f4afe71a4b516c759c21268f51dc))
* update copy on homepage ([23f7853](https://github.com/engineervix/zed-news/commit/23f785315bb5fb84d6207804d46ba27fd62a3911))
* update cron script ([4bdeed6](https://github.com/engineervix/zed-news/commit/4bdeed6f8e5e2e5ae55b1ba7d6b504b0c4694654))
* update info, fix order of news items plus some small ui fixes ([3687fb4](https://github.com/engineervix/zed-news/commit/3687fb4e634ab3aec89b87f9db07106b8e6e57aa))
* use commit-and-tag-version instead of standard-version ([321e842](https://github.com/engineervix/zed-news/commit/321e842cb02f422a0b4a2b2e67cc5f425fd44c03))
* we don't need ffmpeg ([8af534a](https://github.com/engineervix/zed-news/commit/8af534a99d0a8cb58ddf8272ec4871a078f47c5d))
* zed news podcast -> zed news, and use updated illustration ([63343a7](https://github.com/engineervix/zed-news/commit/63343a78475809ab88479892921ba8f97f57d6a4))


### ✅ Tests

* update tests and remove ones we no longer need ([258dad1](https://github.com/engineervix/zed-news/commit/258dad19c3327c7ee93ddb47df0e21a83a8dc83f))


### ⚙️ Build System

* add missing GEMINI_API_KEY ([afd0441](https://github.com/engineervix/zed-news/commit/afd04418e55ffc4c131b2f2f12b630a95bed04fe))
* **deps:** update babel monorepo ([#153](https://github.com/engineervix/zed-news/issues/153)) ([11471dd](https://github.com/engineervix/zed-news/commit/11471dd8dcc47e155742daad830f15eca4a69429))
* **deps:** update dependency babel-loader to v9.2.1 ([#154](https://github.com/engineervix/zed-news/issues/154)) ([4dc8fa6](https://github.com/engineervix/zed-news/commit/4dc8fa6237b62e14e8a3dfa0b360b071ac8ee1df))
* **deps:** update dependency commitizen to v4.3.1 ([#130](https://github.com/engineervix/zed-news/issues/130)) ([d31f16a](https://github.com/engineervix/zed-news/commit/d31f16aef1e0a781a24f87fe9c0359430c3aed87))
* **deps:** update dependency core-js to v3.42.0 ([#155](https://github.com/engineervix/zed-news/issues/155)) ([fd240a4](https://github.com/engineervix/zed-news/commit/fd240a4d81499a560a09258cb9f1393de1d0d73c))
* **deps:** update dependency eslint to v8.57.1 ([#132](https://github.com/engineervix/zed-news/issues/132)) ([32559c5](https://github.com/engineervix/zed-news/commit/32559c5f98df8be1384e19ccb2be89c5cfb344dc))
* **deps:** update dependency mini-css-extract-plugin to v2.9.2 ([#117](https://github.com/engineervix/zed-news/issues/117)) ([5e47e2e](https://github.com/engineervix/zed-news/commit/5e47e2e35160845a9106f934c572977180346539))
* **dev-deps:** bump several dev dependencies to latest versions ([fae82ad](https://github.com/engineervix/zed-news/commit/fae82ad272d5b361b87d84f5e06fda02d864734d))
* just say postgres 15, not 15.xx ([0c91099](https://github.com/engineervix/zed-news/commit/0c910998fffcee7c8c4c9308910fcf8a200a258c))
* remove boto3, id3 and mutagen ([8f73c98](https://github.com/engineervix/zed-news/commit/8f73c98bad4c538eab48ba0e2d70ae6a8db3f3b7))
* things changed in ubuntu 24.04 ([0f1b5c1](https://github.com/engineervix/zed-news/commit/0f1b5c1c70ef6e5366c9f515a8742ecae0a2c44c))


### 👷 CI/CD

* update config ([724edcb](https://github.com/engineervix/zed-news/commit/724edcb0011be93f0fb34fcaf91a049b7f979432))

## [v0.10.0](https://github.com/engineervix/zed-news/compare/v0.9.0...v0.10.0) (2025-05-19)


### 🚀 Features

* attempt to use meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo ([27c2e18](https://github.com/engineervix/zed-news/commit/27c2e18215eae01122183dc1be8953098da226d4))
* create video using SadTalker ([a6ec058](https://github.com/engineervix/zed-news/commit/a6ec058f9c71167450a387d83953799c745e7284))
* dark mode ([11a15a6](https://github.com/engineervix/zed-news/commit/11a15a6032ae02241302b2e3309ed4c5ccb3fb7f))
* dark mode logo ([b003046](https://github.com/engineervix/zed-news/commit/b0030468addc64816a6542c6bfd7935e358bcfec))
* special milestones ([0909a6d](https://github.com/engineervix/zed-news/commit/0909a6df1f3fdc53114356cb8f6677db24bc159b))
* use Meta Llama 3.1 and update prompt ([e04fe6c](https://github.com/engineervix/zed-news/commit/e04fe6c49895a4296e24d08e0139168a0a78d1ea))
* use meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo ([f972307](https://github.com/engineervix/zed-news/commit/f9723072564b9e771f694cef6c6a6ed0adf794a7))


### 💄 Styling

* add dark mode styling for footer and episode links ([5374031](https://github.com/engineervix/zed-news/commit/537403144760aab84b571838f8c1cd028b07a93f))
* improve colours on icon, dark-mode toggle and header img ([f9715fe](https://github.com/engineervix/zed-news/commit/f9715fe7920ae26c3ccbfa9bb01395a71d4de944))
* plyr dark mode ([c1ea409](https://github.com/engineervix/zed-news/commit/c1ea409a363cb0f35f15deae34161692e0d9733e))


### 🐛 Bug Fixes

* add missing namespace to model name ([0e56436](https://github.com/engineervix/zed-news/commit/0e56436e408d7499642042c80d4c177e3c15ed92))
* broken og:image ([6b3430a](https://github.com/engineervix/zed-news/commit/6b3430aefb4c7b914cca4ec7be4d5dd9d8c728ef))
* broken YAML due to double quotes inside description ([fcb7273](https://github.com/engineervix/zed-news/commit/fcb7273ec0f57395fd44fd51518dd1b116506da7))
* broken yaml file ([4b0146f](https://github.com/engineervix/zed-news/commit/4b0146fb9657dcb0bab535800ee612b20ff03f05))
* **deps:** update dependency bootstrap to v5.3.6 ([#148](https://github.com/engineervix/zed-news/issues/148)) ([5dcaf4c](https://github.com/engineervix/zed-news/commit/5dcaf4c0a5130eeced1a82a2e4c9e84cb440ae8f))
* **deps:** update dependency scipy to v1.15.3 ([#149](https://github.com/engineervix/zed-news/issues/149)) ([3e00c0d](https://github.com/engineervix/zed-news/commit/3e00c0dc66daab8aea9002eed9a1af5b9971ddf3))
* **deps:** update dependency ua-parser-js to v1.0.40 ([#150](https://github.com/engineervix/zed-news/issues/150)) ([0cb6275](https://github.com/engineervix/zed-news/commit/0cb62753b7377e672312864d94cbf9ca5394fd50))
* **deps:** update dependency vastai to v0.2.9 ([#151](https://github.com/engineervix/zed-news/issues/151)) ([82033ed](https://github.com/engineervix/zed-news/commit/82033ed2e74489cbd77c3f002ad24efd05eea82b))
* ensure the .env file is loaded correctly ([26793d9](https://github.com/engineervix/zed-news/commit/26793d97a99ce725cf494fe4405566a30ca0497a))
* episode metadata ([4521285](https://github.com/engineervix/zed-news/commit/45212854cb824ac76180b7aa39d246b365a4d0fa))
* handle ServiceUnavailableErrors ([cc3fe63](https://github.com/engineervix/zed-news/commit/cc3fe6388079df0cfb2cd59252361980ce1f3131))
* json string serialization ([ff8c8ca](https://github.com/engineervix/zed-news/commit/ff8c8ca49332a8a195acafad6f38da879e9b43db))
* run the facebook_post task using module notation ([8ee1ea5](https://github.com/engineervix/zed-news/commit/8ee1ea52e1abbafa113edca1052d4a1306b3453e))
* update layout depending on available metadata ([3f9b4ba](https://github.com/engineervix/zed-news/commit/3f9b4ba6d5e075f74b5b7a9759a60795c2e5956e))
* video filename ([4a50325](https://github.com/engineervix/zed-news/commit/4a50325d52fcee2ad05a1ff91fb50ea70859ea43))
* yaml ([8b2f8b0](https://github.com/engineervix/zed-news/commit/8b2f8b063be825706c2e2d49de8de67b6658c819))
* YAML ([0c925db](https://github.com/engineervix/zed-news/commit/0c925db200b1c32ef33e1397eef951f4156da4a0))


### ⚙️ Build System

* add missing scipy ([f2a2a88](https://github.com/engineervix/zed-news/commit/f2a2a88a37fbbe22bf913be295df554c1e314178))
* add more files to dockerignore list ([374d92f](https://github.com/engineervix/zed-news/commit/374d92f4a6ed4e1e98e834457d7614c20b0abbc9))
* bump openai to latest version as of 2024-09-11 ([ab2e4e4](https://github.com/engineervix/zed-news/commit/ab2e4e481df170fea9addfeeb9b574144edbc669))
* **deps-dev:** update dependency babel to v2.15.0 ([#108](https://github.com/engineervix/zed-news/issues/108)) ([caf2a94](https://github.com/engineervix/zed-news/commit/caf2a945886419a3be8ace1c65d2c6fecee26fea))
* **deps-dev:** update dependency dotenv to v16.5.0 ([#131](https://github.com/engineervix/zed-news/issues/131)) ([34b633b](https://github.com/engineervix/zed-news/commit/34b633b9de3871bb3964100527021b2846f67e85))
* **deps-dev:** update dependency postcss-custom-properties to v13.3.12 ([#98](https://github.com/engineervix/zed-news/issues/98)) ([2de6c86](https://github.com/engineervix/zed-news/commit/2de6c867a777e819d8173f1db1ba0caa3df04d6b))
* **deps-dev:** update dependency postcss-loader to v7.3.4 ([#136](https://github.com/engineervix/zed-news/issues/136)) ([2804348](https://github.com/engineervix/zed-news/commit/2804348960de236c397832f88e65480ef7fa1966))
* **deps-dev:** update dependency postcss-preset-env to v8.5.1 ([#99](https://github.com/engineervix/zed-news/issues/99)) ([98afb6f](https://github.com/engineervix/zed-news/commit/98afb6f78455e9bd26fb201f72392844a1effe14))
* **deps-dev:** update dependency pre-commit to v3.7.1 ([#100](https://github.com/engineervix/zed-news/issues/100)) ([a2e8ce7](https://github.com/engineervix/zed-news/commit/a2e8ce75524a74197414aa02107f78696f163853))
* **deps-dev:** update dependency rimraf to v5.0.10 ([#137](https://github.com/engineervix/zed-news/issues/137)) ([1293ea5](https://github.com/engineervix/zed-news/commit/1293ea5bf7f010aec1091ae338c56093714dfb50))
* **deps-dev:** update dependency stylelint to v15.11.0 ([#102](https://github.com/engineervix/zed-news/issues/102)) ([ac3348b](https://github.com/engineervix/zed-news/commit/ac3348bb96624f4f93ae204cf4ebbd81bdde408c))
* **deps-dev:** update dependency webpack to v5.93.0 ([#103](https://github.com/engineervix/zed-news/issues/103)) ([279d88e](https://github.com/engineervix/zed-news/commit/279d88ecaaf8526c69fa26cd21dd8eeb89872723))
* **deps-dev:** update sosedoff/pgweb docker tag to v0.15.0 ([#105](https://github.com/engineervix/zed-news/issues/105)) ([18f7bb4](https://github.com/engineervix/zed-news/commit/18f7bb4b647710f4e11a454e7f11163b90ba6f3c))
* **deps:** update babel monorepo ([#79](https://github.com/engineervix/zed-news/issues/79)) ([4940405](https://github.com/engineervix/zed-news/commit/494040562d0f51eaf6fca84e14a6893c8b922b68))
* **deps:** update dependency @fortawesome/fontawesome-free to v6.6.0 ([#106](https://github.com/engineervix/zed-news/issues/106)) ([8123136](https://github.com/engineervix/zed-news/commit/81231369ba66e0b763050c76766f30a271ba16a4))
* **deps:** update dependency apprise to v1.8.0 ([#107](https://github.com/engineervix/zed-news/issues/107)) ([0e6318c](https://github.com/engineervix/zed-news/commit/0e6318c3a65cd0d5e06e9056ddaba67bad4ba42d))
* **deps:** update dependency bootstrap to v5.3.5 ([#138](https://github.com/engineervix/zed-news/issues/138)) ([935f93b](https://github.com/engineervix/zed-news/commit/935f93b51f3ad8d9e42904fedaa293ded1ea31be))
* **deps:** update dependency cohere to v4.57 ([#109](https://github.com/engineervix/zed-news/issues/109)) ([4ac038e](https://github.com/engineervix/zed-news/commit/4ac038e21480dfaf2bc0a9a60a9ff637cc28b562))
* **deps:** update dependency eyed3 to v0.9.8 ([#144](https://github.com/engineervix/zed-news/issues/144)) ([5ebe650](https://github.com/engineervix/zed-news/commit/5ebe650563070df59c168f5588af0a5a80aef066))
* **deps:** update dependency fake-useragent to v1.5.1 ([#110](https://github.com/engineervix/zed-news/issues/110)) ([e287438](https://github.com/engineervix/zed-news/commit/e287438c12d1796316428f101b1e25b505b4218e))
* **deps:** update dependency invoke to v2.2.0 ([#111](https://github.com/engineervix/zed-news/issues/111)) ([0236930](https://github.com/engineervix/zed-news/commit/02369308d939392c51ab75c94bdff80c77e983c7))
* **deps:** update dependency jinja2 to v3.1.6 [security] ([#133](https://github.com/engineervix/zed-news/issues/133)) ([2198f81](https://github.com/engineervix/zed-news/commit/2198f814282c7822b2a23e91e74b1a224edefbd8))
* **deps:** update dependency langchain to v0.3.24 ([#139](https://github.com/engineervix/zed-news/issues/139)) ([dca658e](https://github.com/engineervix/zed-news/commit/dca658e7ef3e7e46e42796dc0d4e0233f894e21b))
* **deps:** update dependency langchain to v0.3.25 ([#145](https://github.com/engineervix/zed-news/issues/145)) ([9e9e666](https://github.com/engineervix/zed-news/commit/9e9e666c68d0f70df9b544752352e19364a413f0))
* **deps:** update dependency langchain-community to v0.3.23 ([#140](https://github.com/engineervix/zed-news/issues/140)) ([e6b3e32](https://github.com/engineervix/zed-news/commit/e6b3e3204704cb38d7e0a15a1f19df5eae9624b0))
* **deps:** update dependency langchain-openai to v0.3.16 ([#141](https://github.com/engineervix/zed-news/issues/141)) ([14a5960](https://github.com/engineervix/zed-news/commit/14a5960a0c6d909386a528af24b17419c3d86179))
* **deps:** update dependency mutagen to v1.47.0 ([#112](https://github.com/engineervix/zed-news/issues/112)) ([4b76bbb](https://github.com/engineervix/zed-news/commit/4b76bbb0b62672de023d5f2cc6962f703d962e9d))
* **deps:** update dependency num2words to v0.5.14 ([#142](https://github.com/engineervix/zed-news/issues/142)) ([c62b49b](https://github.com/engineervix/zed-news/commit/c62b49b4361c02134bdb67fffb66f62419e3c140))
* **deps:** update dependency peewee to v3.17.9 ([#128](https://github.com/engineervix/zed-news/issues/128)) ([3a93449](https://github.com/engineervix/zed-news/commit/3a9344912342f544338cda1e355d2799098de053))
* **deps:** update dependency python-dateutil to v2.9.0 ([#114](https://github.com/engineervix/zed-news/issues/114)) ([421c2fa](https://github.com/engineervix/zed-news/commit/421c2fac8621e9c4fc82fc6367ed59c525214bec))
* **deps:** update dependency scipy to v1.15.2 ([#143](https://github.com/engineervix/zed-news/issues/143)) ([3353d56](https://github.com/engineervix/zed-news/commit/3353d56a543c0f1050fea7684796d9bac1a3725f))
* **deps:** update dependency sharer.js to v0.5.3 ([#146](https://github.com/engineervix/zed-news/issues/146)) ([c142a00](https://github.com/engineervix/zed-news/commit/c142a006c5d9e9c60cee15be7966c9273f91276f))
* **deps:** update dependency together to v1.5.5 ([#121](https://github.com/engineervix/zed-news/issues/121)) ([c79154e](https://github.com/engineervix/zed-news/commit/c79154ef6543023a44d2671c36de71b60ddaa697))
* **deps:** update dependency torch to v2.2.0 [security] ([#115](https://github.com/engineervix/zed-news/issues/115)) ([60d6301](https://github.com/engineervix/zed-news/commit/60d630151a5d0fb1a5136939fa0ef61f562ed8ec))
* **deps:** update dependency torch to v2.6.0 [security] ([#135](https://github.com/engineervix/zed-news/issues/135)) ([980b191](https://github.com/engineervix/zed-news/commit/980b191099ad8ec79d797c70ed6376b3e08ede9b))
* **deps:** update dependency transformers to v4.48.0 [security] ([#134](https://github.com/engineervix/zed-news/issues/134)) ([2559765](https://github.com/engineervix/zed-news/commit/255976575511917e666d6d060d7425073323a57f))
* **deps:** update dependency transformers to v4.51.3 ([#147](https://github.com/engineervix/zed-news/issues/147)) ([b2f7e89](https://github.com/engineervix/zed-news/commit/b2f7e8967cd5bc4c05c2311210231cc52d22f0b4))
* **deps:** update dependency webpack to v5.94.0 [security] ([#116](https://github.com/engineervix/zed-news/issues/116)) ([40cd1bc](https://github.com/engineervix/zed-news/commit/40cd1bcd8a4739265cce9f54cb53311ba326fb94))
* **deps:** update postgres docker tag to v15.8 ([#104](https://github.com/engineervix/zed-news/issues/104)) ([a77db10](https://github.com/engineervix/zed-news/commit/a77db10cc928548a43c12c533ebc69e59490b35b))
* ensure moviepy is specified as a dependency ([b17f952](https://github.com/engineervix/zed-news/commit/b17f9523d922f9ce4304d43920b8a8657276a389))
* google-genai ([2886675](https://github.com/engineervix/zed-news/commit/2886675cd5391362f0f607a19e364f07298f2e6b))
* install vastai CLi tool ([1517e97](https://github.com/engineervix/zed-news/commit/1517e97625ca74d0557aa8377e6150f0d684209c))
* update dependencies ([9f73318](https://github.com/engineervix/zed-news/commit/9f73318990cee092d888d6aadce81b4a89b94806))
* upgrade to python 3.12 and ubuntu 24.04 ([8ffb01f](https://github.com/engineervix/zed-news/commit/8ffb01f41ca797a78282cc3b1dc946bd2ee311b5))


### ♻️ Code Refactoring

* a simpler way to generate videos ([d3e5293](https://github.com/engineervix/zed-news/commit/d3e5293921eee57fccd2a8f410f2419477c662e2))
* add newer GPT model, improve prompt, fix black config ([a3327b1](https://github.com/engineervix/zed-news/commit/a3327b163ea54db69611c316da3600139b52adf4))
* be more specific when commiting changes ([209812f](https://github.com/engineervix/zed-news/commit/209812f5af3a072c0dc2549b9372d9bae6e043c4))
* conditionally show some time stats ([0f1ff17](https://github.com/engineervix/zed-news/commit/0f1ff17fc353c31e59bab112a40ca13e7dd5a34f))
* dark mode -- navbar and header ([bff2e8a](https://github.com/engineervix/zed-news/commit/bff2e8a394fcd4e821473231f0c3e0c8569ab304))
* improve dark mode implementation ([bafae15](https://github.com/engineervix/zed-news/commit/bafae155e579bf2541fd295e6c6d76663a7eb580))
* improve prompt and cleanup ([b300faa](https://github.com/engineervix/zed-news/commit/b300faa926c54cb04667a94f10673941764f7d00))
* **make_video.sh:** ensure that the python virtual environment is activated ([98a7bcd](https://github.com/engineervix/zed-news/commit/98a7bcdd51d18e54abae1a1c52bf13845a6452b3))
* simplify video creation ([643393b](https://github.com/engineervix/zed-news/commit/643393b159a1643aa72628b8d8b8acc238f561fe))
* SSH key id to be more unique ([7964af0](https://github.com/engineervix/zed-news/commit/7964af09838b423b371776cf391af6593a4ec2bf))
* synthesize rather than summarise ([f6bb372](https://github.com/engineervix/zed-news/commit/f6bb372add869bc7b33328929cd6b28ce41f8e65))
* udpate models and fix invocation of get_episode_number ([e446f03](https://github.com/engineervix/zed-news/commit/e446f034df1709126c022de7e968b162f341f15f))
* use `mistralai/Mixtral-8x7B-v0.1` for summaries ([b9edb7f](https://github.com/engineervix/zed-news/commit/b9edb7f6b75d7b6829486cbddf5e355de1d7a5c9))
* use client.chat.completions everywhere ([f9803c3](https://github.com/engineervix/zed-news/commit/f9803c373a5b27be8bbed5c240e3e9caed45a119))
* use Google's Gemini API for podcast episode summary ([52e99cd](https://github.com/engineervix/zed-news/commit/52e99cd7673d805387010289ced3c45f976f42bf))
* use mistralai/Mixtral-8x7B-v0.1 for everything else ([fc918ac](https://github.com/engineervix/zed-news/commit/fc918ac194ff06757dabad01fefdd7426645152b))
* use mistralai/Mixtral-8x7B-v0.1 instead of garage-bAInd/Platypus2-70B-instruct for individual articles ([25b3dab](https://github.com/engineervix/zed-news/commit/25b3dab8031848e83c132c48de1273ada7ab0287))
* use Mixtral-8x22B-Instruct-v0.1 for article summarisation ([da0d675](https://github.com/engineervix/zed-news/commit/da0d6753c6fa4a4c66f142047b9ad86173cd2e9a))
* use ntfy.sh for notifications ([504aed6](https://github.com/engineervix/zed-news/commit/504aed6eb3ae65b49927b073742a69e04cef6f6a))
* use openai for the transcript, and update prompts ([99a1ff6](https://github.com/engineervix/zed-news/commit/99a1ff6775636f8a0d11abd47a86dab05b86c82e))
* use updated langchain openai package ([0a379ad](https://github.com/engineervix/zed-news/commit/0a379adaa1dfed3c7e6b94d68595019e0e7771bc))


### ✅ Tests

* add tests for social posting ([3c751c1](https://github.com/engineervix/zed-news/commit/3c751c17b79b1b6e1da6a85387d4fafff37e71ee))
* add unit tests for together summarization ([86359e4](https://github.com/engineervix/zed-news/commit/86359e4c0d10d4d33c36a18017db71992441ab05))
* fix broken test ([eca18b3](https://github.com/engineervix/zed-news/commit/eca18b37d7095378c5695ffe7e45323c6a0729da))
* fix broken test after 45212854cb824ac76180b7aa39d246b365a4d0fa ([823b40a](https://github.com/engineervix/zed-news/commit/823b40ae49c5eb74c5096a48cdefa8b88feb3da2))
* write more unit tests ([9c95809](https://github.com/engineervix/zed-news/commit/9c958095cae50b2b4f2fa920a2d5c7fe36547ff2))
* write unit tests for summarization ([14d1d0b](https://github.com/engineervix/zed-news/commit/14d1d0b98832c37473507462b27a8c421f97b4cc))


### 👷 CI/CD

* add missing GEMINI_API_KEY ([60443be](https://github.com/engineervix/zed-news/commit/60443befda2812d94de1c1f2fcfca2807695f2a4))
* ensure proper venv creation and activation in GitHub Actions ([dac0f04](https://github.com/engineervix/zed-news/commit/dac0f0417080fded30c86c93567b527ba01b13d0))
* ensure sass is not updated, for now ([6361917](https://github.com/engineervix/zed-news/commit/6361917471df4445d99ca7f705f72ca98a9ad466)), closes [twbs/bootstrap#34051](https://github.com/twbs/bootstrap/issues/34051)
* fix failing tests ([8366ce1](https://github.com/engineervix/zed-news/commit/8366ce10ad446e6c7fb1465707935807ecbbfd79))

## [v0.9.0](https://github.com/engineervix/zed-news/compare/v0.8.0...v0.9.0) (2024-07-20)


### 💄 Styling

* change support image ([795a860](https://github.com/engineervix/zed-news/commit/795a860752b95e59e67ecf86e8224905bac9e5cb))


### 🐛 Bug Fixes

* correct usage of together v1.2.x completions API ([4d5c7a6](https://github.com/engineervix/zed-news/commit/4d5c7a6847657c42e8fd834792a862e235209e36))
* **deps:** update dependency boto3 to v1.34.145 ([c232eda](https://github.com/engineervix/zed-news/commit/c232eda702b8bc4cdb054dbc54ebf863a91b9f74))
* **deps:** update dependency ua-parser-js to v1.0.38 ([c9616dc](https://github.com/engineervix/zed-news/commit/c9616dc9205bdf1424d9305fbea09a72738baf1c))
* use together v1.2.x and the Chat interface ([415c7fd](https://github.com/engineervix/zed-news/commit/415c7fd338ab47128d099d04f3020a3604392db1))


### 📝 Docs

* add diagram that illustrates how the whole thing works ([f4582f3](https://github.com/engineervix/zed-news/commit/f4582f3c62769152e0948d6c9bc5cfc272526d21))
* update news sources ([7d6fe82](https://github.com/engineervix/zed-news/commit/7d6fe824627454e6b5d32ec7185d2b4ee230d6ec))


### 👷 CI/CD

* bump schneegans/dynamic-badges-action to v1.7.0 ([fd122b4](https://github.com/engineervix/zed-news/commit/fd122b47c0594ee271ba03b58a7d2d71102f376f))
* ensure TOGETHER_API_KEY environment variable exists ([fa71dad](https://github.com/engineervix/zed-news/commit/fa71dadd2819c69d49fa77fb395e12669a59abf5))
* improve CI ([aaeaf67](https://github.com/engineervix/zed-news/commit/aaeaf6797abe6f3cb04e70a5702da4809b216700))


### 🚀 Features

* apply Dynamic Range Compression ([280e1d4](https://github.com/engineervix/zed-news/commit/280e1d46572326cf4ffbebebc7ca7602c9aa3bb5))
* improve audio quality and only use 1 audio file for background music ([d8b2131](https://github.com/engineervix/zed-news/commit/d8b21316b6f358606c3945ea05228021ea8c013d))
* the one where Ayanda returns from her hiatus ([e775906](https://github.com/engineervix/zed-news/commit/e775906dfa38297933c8a51fb43f1876638e52b6))
* use meta-llama/Llama-3-70b-chat-hf ([12fbe27](https://github.com/engineervix/zed-news/commit/12fbe27e0eceedc0a175d80ab2be80f7f60ae69a))


### ✅ Tests

* update tests in light of d8b2131, 3166486 and 280e1d4 ([070d3ff](https://github.com/engineervix/zed-news/commit/070d3ff3884c2e0c1de432f8b5c625ac9c4855f4))


### ♻️ Code Refactoring

* bump summary limits ([0c33424](https://github.com/engineervix/zed-news/commit/0c3342488b0ccd1ef8eebb73c1f39ed2612a5842))
* change intro and outro music ([ab3877f](https://github.com/engineervix/zed-news/commit/ab3877fba3d34279c7d7a0d04230754a6918b78b))
* darken overlay, brighten txt, use smaller & more apt bg image ([66880b5](https://github.com/engineervix/zed-news/commit/66880b56be0016edc8d7ad3cfcd37b31a7f758d4))
* switch from Google Podcasts to Spotify ([4313912](https://github.com/engineervix/zed-news/commit/4313912de250929006c62169ef60484e97f5135e))
* update some text on about page ([35ef4bb](https://github.com/engineervix/zed-news/commit/35ef4bba6165e053a619cbefcc4a7271253b5cf6))
* update transcript creation prompt ([544f30c](https://github.com/engineervix/zed-news/commit/544f30c15bb6b8a0d66909b07d267f532e73c319))
* use actual podcast transcript to generate description ([3166486](https://github.com/engineervix/zed-news/commit/3166486ea14c95e89cfcda15ea39f38703dfd270))
* use older/newer instead of next/previous ([d685379](https://github.com/engineervix/zed-news/commit/d68537971cbc748f49d809a16b5793315df11160))
* we no longer need to specify version in docker compose config ([0d48eb0](https://github.com/engineervix/zed-news/commit/0d48eb0e5eff81252fe64fe7f952e89d08923fba))


### ⚙️ Build System

* bump Node.js to version 18 ([8ac7d09](https://github.com/engineervix/zed-news/commit/8ac7d09bdce7e3da1943721e776d026756a67223))
* bump poetry to 1.8.3 ([7d4a871](https://github.com/engineervix/zed-news/commit/7d4a8719d7312d719630cffe81a6ff78d04b1384))
* **deps-dev:** update dependency eslint to v8.57.0 ([#92](https://github.com/engineervix/zed-news/issues/92)) ([0f9ab59](https://github.com/engineervix/zed-news/commit/0f9ab5938c40c8da51822b65989e3312270664b8))
* **deps-dev:** update dependency eslint-config-prettier to v8.10.0 ([#93](https://github.com/engineervix/zed-news/issues/93)) ([7dd8528](https://github.com/engineervix/zed-news/commit/7dd85283e6aa662160fb94f9c762e5c79dbca53e))
* **deps-dev:** update dependency eslint-webpack-plugin to v4.2.0 ([#94](https://github.com/engineervix/zed-news/issues/94)) ([37f5d44](https://github.com/engineervix/zed-news/commit/37f5d44818256aa880eaee723934c38b9e10b6ec))
* **deps-dev:** update dependency mini-css-extract-plugin to v2.9.0 ([#95](https://github.com/engineervix/zed-news/issues/95)) ([b7dbe51](https://github.com/engineervix/zed-news/commit/b7dbe51e0bb58dcae09d6754b310c4baeb87ad8e))
* **deps:** replace dependency npm-run-all with npm-run-all2 ^5.0.0 ([#69](https://github.com/engineervix/zed-news/issues/69)) ([02c9b22](https://github.com/engineervix/zed-news/commit/02c9b22ce7a8e8f57a226dcccd761ea591c9b21b))
* **deps:** update dependency bootstrap to v5.3.3 ([#71](https://github.com/engineervix/zed-news/issues/71)) ([42b92b9](https://github.com/engineervix/zed-news/commit/42b92b99ecf6ad060a08c6a99e2213e494310901))
* **deps:** update dependency boto3 to v1.34.136 ([#72](https://github.com/engineervix/zed-news/issues/72)) ([5932716](https://github.com/engineervix/zed-news/commit/59327168b20c83d60fe968c8cc8b26a82ced6e8b))
* **deps:** update dependency commitizen to v3.27.0 ([#75](https://github.com/engineervix/zed-news/issues/75)) ([bc1e505](https://github.com/engineervix/zed-news/commit/bc1e505fdf033f5ea501329b8edb8002de89eb4d))
* **deps:** update dependency commitizen to v3.28.0 ([#91](https://github.com/engineervix/zed-news/issues/91)) ([ed3fd4d](https://github.com/engineervix/zed-news/commit/ed3fd4d4d9e5f7ab1cc6c46cc8f9d62fa8a62e78))
* **deps:** update dependency css-loader to v6.11.0 ([#86](https://github.com/engineervix/zed-news/issues/86)) ([a6d8955](https://github.com/engineervix/zed-news/commit/a6d8955d7ffa9b311b49916613c0d7defee5c891))
* **deps:** update dependency cssnano to v6.1.2 ([#76](https://github.com/engineervix/zed-news/issues/76)) ([a77a048](https://github.com/engineervix/zed-news/commit/a77a048e217ac427a3e239a05ffaf2af8eab3994))
* **deps:** update dependency del to v7.1.0 ([#77](https://github.com/engineervix/zed-news/issues/77)) ([beca01c](https://github.com/engineervix/zed-news/commit/beca01cd584b8b5ef1332c8efc6542779739408e))
* **deps:** update dependency dotenv to v16.4.5 ([#87](https://github.com/engineervix/zed-news/issues/87)) ([445744f](https://github.com/engineervix/zed-news/commit/445744fb344b0cc53cfcb416d5ff0de75a603f97))
* **deps:** update dependency jinja2 to v3.1.4 ([#83](https://github.com/engineervix/zed-news/issues/83)) ([32faf57](https://github.com/engineervix/zed-news/commit/32faf578bbb34db2f5e100f0a5c521b862bd75bd))
* **deps:** update dependency peewee to v3.17.5 ([#73](https://github.com/engineervix/zed-news/issues/73)) ([1b5d917](https://github.com/engineervix/zed-news/commit/1b5d917fa0552ada9b2aecaa33285f0322ba0ac2))
* **deps:** update dependency peewee to v3.17.6 ([#88](https://github.com/engineervix/zed-news/issues/88)) ([7324a49](https://github.com/engineervix/zed-news/commit/7324a495900191246e2108f7b9384f3e34c3240c))
* **deps:** update dependency postcss to v8.4.39 ([#70](https://github.com/engineervix/zed-news/issues/70)) ([5dea587](https://github.com/engineervix/zed-news/commit/5dea587deb5d997c6ccbd6d37a8e2594d2d7f572))
* **deps:** update dependency python-dotenv to v1.0.1 ([#74](https://github.com/engineervix/zed-news/issues/74)) ([5c6cd1a](https://github.com/engineervix/zed-news/commit/5c6cd1a7ca018b3e64b54255ec107cb0e9bef474))
* **deps:** update dependency requests to v2.32.2 [security] ([#78](https://github.com/engineervix/zed-news/issues/78)) ([bc12059](https://github.com/engineervix/zed-news/commit/bc12059ebfa31b2edea214b5ef9cad85a6d8e4dd))
* **deps:** update dependency sharer.js to v0.5.2 ([#89](https://github.com/engineervix/zed-news/issues/89)) ([5fb25aa](https://github.com/engineervix/zed-news/commit/5fb25aa6746975b430fd2f7a572a18fcd137bdcf))
* **deps:** update dependency together to v1.2.2 ([#90](https://github.com/engineervix/zed-news/issues/90)) ([19d7649](https://github.com/engineervix/zed-news/commit/19d76499b80abc2c24da5543cd49fcdaece3cc82))
* remove html-minifier because of security vulnerabilities ([b89bd99](https://github.com/engineervix/zed-news/commit/b89bd99b8d712a25b6f72adb26efdea8dcbaea0e))
* update black (23.12.1 -> 24.4.2) ([9d7619b](https://github.com/engineervix/zed-news/commit/9d7619bdb49d546ee812e53493aadc2a06752463))
* update certifi (2023.5.7 -> 2024.7.4) ([ffa96fa](https://github.com/engineervix/zed-news/commit/ffa96fae06eebbc222e920bd4fb4b7769a254c9c))
* update idna (3.4 -> 3.7) ([9db73ee](https://github.com/engineervix/zed-news/commit/9db73ee5f97eb0bab2c40b548c13ed1f0a7ceea7))
* update langchain (0.0.353 -> 0.2.10) ([da3a9f9](https://github.com/engineervix/zed-news/commit/da3a9f964c012198f05007994dac86a962c50bd6))
* update requests (2.31.0 -> 2.32.3) ([aaf5bbb](https://github.com/engineervix/zed-news/commit/aaf5bbb666a0ee9625cb579ff26ebbaf07fc9b66))
* update ruff (0.0.291 -> 0.5.3) ([7b767ba](https://github.com/engineervix/zed-news/commit/7b767ba8320a95753f4bcca69a166a5e46525428))
* update setuptools (67.8.0 -> 71.0.4) ([f099997](https://github.com/engineervix/zed-news/commit/f099997b761937db470b13bdb73989058291fc59))
* update transformers (4.36.2 -> 4.42.4) ([02f4011](https://github.com/engineervix/zed-news/commit/02f4011fb599edfa1acdf3fdcc58e7639515dfcb))
* update urllib3 (1.26.16 -> 2.2.2) ([7b83a7f](https://github.com/engineervix/zed-news/commit/7b83a7ffae1e0463dd96151255dbdd013da500dc))
* update zipp (3.15.0 -> 3.19.2) ([6b512e0](https://github.com/engineervix/zed-news/commit/6b512e0098c8809d3632615e5d859e7fc08f4c19))

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
