# zed-news

> Automated news podcast consisting of AI-powered updates from various Zambian 🇿🇲 sources.

[![made-with-python](https://forthebadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![made-with-javascript](https://forthebadge.com/images/badges/made-with-javascript.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

[![CI/CD](https://github.com/engineervix/zed-news/actions/workflows/main.yml/badge.svg)](https://github.com/engineervix/zed-news/actions/workflows/main.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/engineervix/f4b1128b188c4e29722bc879e4ab6574/raw/covbadge.json)](https://github.com/engineervix/zed-news/actions?query=workflow%3A%22CI%2FCD%22)
[![healthchecks.io](https://healthchecks.io/badge/24d88c7e-cc91-4dac-b9a5-d50e52/ewRXZ-TO/zed-news.svg)](https://healthchecks.io)

[![python3](https://img.shields.io/badge/python-3.10-brightgreen.svg)](https://www.python.org/downloads/)
[![Node v18](https://img.shields.io/badge/Node-v18-teal.svg)](https://nodejs.org/en/blog/release/v18.0.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![code style: prettier](https://img.shields.io/badge/code%20style-prettier-ff69b4.svg)](https://prettier.io/)

[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)
[![Conventional Changelog](https://img.shields.io/badge/changelog-conventional-brightgreen.svg)](http://conventional-changelog.github.io)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Why this project?](#why-this-project)
- [Development](#development)
  - [Core](#core)
  - [Web](#web)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [TODO](#todo)
  - [Docs](#docs)
  - [Dev](#dev)
  - [Frontend (Web)](#frontend-web)
  - [Backend (Core)](#backend-core)
  - [Features for future releases](#features-for-future-releases)
- [Credits](#credits)
  - [Music](#music)
  - [Icon](#icon)
  - [News Sources](#news-sources)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This is a tool that gathers news from various Zambian 🇿🇲 sources, summarizes the news items and presents the news as a podcast.

It consists primarily of two parts / components:

- **core** -- this is primarily python code, where the following tasks are handled:

  - gather the news using [requests](https://pypi.org/project/requests/), [feedparser](https://pypi.org/project/feedparser/) and [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
  - summarise the news using LLMs,
  - create the podcast transcript,
  - convert text to speech using [AWS Polly](https://aws.amazon.com/polly/),
  - process the audio using [ffmpeg](https://ffmpeg.org/), and
  - generate content for the website.

  The illustration below summarises this:

  ![How it works](https://res.cloudinary.com/engineervix/image/upload/v1697574721/slidev/zed-news-talk/toolchain.png)

- **web** -- this is an [11ty](https://www.11ty.dev/) project, consisting of logic to build a static site for the podcast, including an RSS feed.

## Why this project?

- I'm generally terrible at keeping up with current affairs
- I wanted to learn how to work with AI tools while solving a real problem
- I was inspired by [Hackercast](https://camrobjones.com/hackercast/)

## Development

- clone / fork the project
- `cd` into the project directory

### Core

> **Note**
>
> You need to have `docker` and `docker-compose` on your machine

On your machine:

- you need to have [poetry](https://python-poetry.org/) installed
- create a python [virtual environment](https://realpython.com/python-virtual-environments-a-primer/)
- upgrade pip to latest version

  ```bash
  pip install --upgrade pip
  ```

- install dependencies

  ```bash
  poetry install
  ```

- update environment variables.

  ```bash
  # copy .env.sample to .env
  cp -v .env.sample .env

  # Now you can update the relevant values in the .env file
  ```

- build images and spin up docker containers

  ```bash
  inv up --build
  ```

- access the `app` container

  ```bash
  inv exec app bash
  ```

In the container:

- you can run tests

  ```bash
  inv test
  ```

- you can run the program

  ```bash
  inv toolchain
  ```

See available [invoke](https://www.pyinvoke.org/) tasks with `invoke -l`

The project uses [pgweb](https://github.com/sosedoff/pgweb) to help visualize database changes. You can access this in your browser at <http://127.0.0.1:8081>

### Web

This project uses Node [v18](https://nodejs.org/en/blog/release/v18.0.0). I recommend using [fnm](https://github.com/Schniz/fnm) or [volta](https://volta.sh/) to simplify managing Node.js versions on your machine.

- install frontend dependencies

  ```bash
  npm install
  ```

- start the dev server, accessible at <http://127.0.0.1:8080/>

  ```bash
  npm start
  ```

See other available scripts in `package.json`.

## Deployment

The final outputs of this project are:

- **mp3 files**, hosted on [AWS S3](https://aws.amazon.com/s3/) (or similar platforms like [Backblaze](https://www.backblaze.com/)).
- **a static site**, which can be hosted anywhere. I use [Cloudflare Pages](https://pages.cloudflare.com/), but you have various options such as [GitGub Pages](https://pages.github.com/), [Netlify](https://www.netlify.com/), [Vercel](https://vercel.com/), [Render](https://render.com/), etc. You can even choose to host it on your own server.

> **Warning**
>
> Ensure that environment variables are updated accordingly for both **core** and **web**.

For a smooth, unattended setup, please follow these steps:

1. Set up a [\*nix](https://en.wikipedia.org/wiki/Unix-like) machine (it can be your laptop, a VPS, etc.) with a Python virtual environment for the project, and make sure `docker` and `docker-compose` are installed.

2. Configure a cron job on the machine to run the `cron.sh` script located in the repository root. This script will handle the automated generation and deployment process.

3. Ensure that the machine has `git` properly configured. This is necessary for the `cron.sh` script to push the generated content to the repository, triggering the build and deployment.

By following these steps, you can automate the deployment process and keep your project up to date without manual intervention.

> **Note**
>
> The `cron.sh` script uses [apprise](https://github.com/caronc/apprise) to notify the owner when a new episode is ready. You'll need to check the apprise docs on how to configure Telegram.
>
> Feel free to adapt the deployment setup to your specific requirements and preferred hosting platforms.

## Contributing

<!-- Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)): -->

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions, issues and feature requests are most welcome! A good place to start is by helping out with the unchecked items in the [TODO](#todo) section of this README!

Feel free to check the [issues page](https://github.com/engineervix/zed-news/issues) and take a look at the [contributing guide](https://github.com/engineervix/zed-news/blob/main/CONTRIBUTING.md) before you get started.

To maintain code quality and formatting consistency, we utilize pre-commit hooks. These hooks automatically check and format your code before each commit. This helps ensure that the codebase remains clean and consistent throughout the development process. Set up the Git pre-commit hooks by running the following

```bash
pre-commit install && pre-commit install --hook-type commit-msg
```

See `pre-commit-config.yaml` for more details. In addition, please note the following:

- if you're making code contributions, please try and write some tests to accompany your code, and ensure that the tests pass. Also, were necessary, update the docs so that they reflect your changes.
- your commit messages should follow the conventions described [here](https://www.conventionalcommits.org/en/v1.0.0/). Write your commit message in the imperative: "Fix bug" and not "Fixed bug" or "Fixes bug".
  Once you are done, please create a [pull request](https://github.com/engineervix/zed-news/pulls).

## TODO

### Dev

- [x] Switch to [Poetry](https://python-poetry.org/)
- [x] Replace [flake8](https://pypi.org/project/flake8/), [pycodestyle](https://pypi.org/project/pydocstyle/) and [isort](https://pypi.org/project/isort/) with [ruff](https://github.com/charliermarsh/ruff)
- [ ] Improve test coverage

### Frontend (Web)

- [x] Create a **More ways to listen** button with a popup/modal so that people can choose multiple services
- [ ] Keep things DRY. For example, the **More ways to listen** modal on the _home_ and _about_ pages, the header and footer icons.
- [ ] Toggle Dark/Light mode
- [ ] Improve the mobile UI. For example, the audio player controls
- [ ] Improve a11y. For instance, learn more about [using the aria-current attribute](https://tink.uk/using-the-aria-current-attribute/)
- [ ] Implement **search** on the web app

### Backend (Core)

- [x] Add a separate module for summarization backends so we can choose which one to work with
- [ ] Add more robust error handling on `requests` and `feedparser` jobs as well as all other operations, such as connecting to AWS Polly, etc.
- [ ] Add task to perform substitution so that, for instance, K400 is written as 400 Kwacha. The AWS Polly voices fail to read Zambian money correctly.

### Features for future releases

- [ ] Add [Diamond TV](https://diamondtvzambia.com) as a news source. Might be a good idea to replace Muvi TV with Diamond TV because the latter seems to have infrequent updates. Also, we don't want too many news items -- it kills the whole point of this project -- to get the latest updates delivered in a _concise_ manner.
- [x] Connect with social media platforms and automagically tweet, post to facebook when a new episode is out.
- [ ] Incorporate a newsletter version where the news is sent to your mailbox in a nice, clean format. People can subscribe / unsubscribe.
- [ ] Mention the weather in Lusaka, Livingstone, Kabwe, etc. Perhaps the weather forecast for the following day?
- [ ] Mention exchange rates
- [x] Cleanup the news by consolidating similar articles from different sources. In other words, let's make this [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself).
- [ ] Find a way of training the voice to learn how to pronounce Zambian words.
- [ ] Find a way to summarize for free, without relying on OpenAI's API. Perhaps train your own model, learn how to leverage tools like [NLTK](https://www.nltk.org/), [spaCy](https://spacy.io/), etc.
- [ ] Find a way to make a closing statement based on the news. Something like, "Don't forget to register yor sim card before the ZICTA deadline ..."
- [ ] Keep the background music running throughout the show
- [ ] Different background music for each day of the week
- [ ] Possibly allow for passing of an argument variable for the voice, or dynamically choose a voice from a list, just like the random intros and outros.

## Credits

### Music

- <https://pixabay.com/music/beats-sweet-breeze-167504/>
- <https://pixabay.com/music/beats-aesthetic-beat-royalty-free-music-215851/>
- <https://pixabay.com/music/beats-digital-technology-131644/>
- <https://pixabay.com/music/beats-stellar-echoes-202315/>
- <https://pixabay.com/music/afrobeat-it-afrobeat-149308/>

### Icon

- logo adapted from <https://www.pngrepo.com/svg/227923/news-reporter-woman>

### News Sources

- [ZNBC](https://znbc.co.zm/)
- [Zambia Daily Mail](http://www.daily-mail.co.zm/)
- [Times of Zambia](https://times.co.zm/)
- [News Diggers!](https://diggers.news/)
- [Muvi TV](https://www.muvitv.com/)
- [Mwebantu](https://www.mwebantu.com/)
