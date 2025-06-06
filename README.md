# zed-news

> Automated news digests from various Zambian 🇿🇲 sources.

[![CI/CD](https://github.com/engineervix/zed-news/actions/workflows/main.yml/badge.svg)](https://github.com/engineervix/zed-news/actions/workflows/main.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/engineervix/f4b1128b188c4e29722bc879e4ab6574/raw/covbadge.json)](https://github.com/engineervix/zed-news/actions?query=workflow%3A%22CI%2FCD%22)
[![healthchecks.io](https://healthchecks.io/badge/24d88c7e-cc91-4dac-b9a5-d50e52/ewRXZ-TO/zed-news.svg)](https://healthchecks.io)

[![python](https://img.shields.io/badge/python-3.12-brightgreen.svg)](https://www.python.org/downloads/)
[![Node v18](https://img.shields.io/badge/Node-v18-teal.svg)](https://nodejs.org/en/blog/release/v18.0.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![code style: prettier](https://img.shields.io/badge/code%20style-prettier-ff69b4.svg)](https://prettier.io/)

[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)
[![Conventional Changelog](https://img.shields.io/badge/changelog-conventional-brightgreen.svg)](http://conventional-changelog.github.io)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Project Evolution: From Podcast to News Digest](#project-evolution-from-podcast-to-news-digest)
- [Development](#development)
  - [Core](#core)
  - [Web](#web)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [TODO](#todo)
  - [Dev](#dev)
  - [Frontend (Web)](#frontend-web)
  - [Features for future releases](#features-for-future-releases)
- [Credits](#credits)
  - [Music](#music)
  - [Icons](#icons)
  - [News Sources](#news-sources)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tool gathers news from various Zambian 🇿🇲 sources, processes them, and presents them as a text-based news digest.

The project has two main components:

- **core** -- A Python application that handles:

  - Gathering news from RSS feeds using [requests](https://pypi.org/project/requests/), [feedparser](https://pypi.org/project/feedparser/), and [beautifulsoup4](https://pypi.org/project/beautifulsoup4/).
  - Processing the news articles using Large Language Models (LLMs).
  - Generating structured data for the static website.

- **web** -- An [11ty](httpss://www.11ty.dev/) static site that presents the news digests.

## Project Evolution: From Podcast to News Digest

After 500 episodes, I decided to transition the Zed News project from generating audio podcast episodes to producing text-based news digests. The core value of providing consolidated Zambian news is still preserved.

The original podcast episodes have been archived, and the project now focuses on delivering fast, scannable news content.

## Development

- Clone or fork the project.
- `cd` into the project directory.

### Core

> **Note**
>
> You need to have `docker` and `docker-compose` on your machine.

- Install [Poetry](https://python-poetry.org/).
- Create a Python [virtual environment](https://realpython.com/python-virtual-environments-a-primer/).
- Install dependencies:
  ```bash
  poetry install
  ```
- Set up environment variables:

  ```bash
  # Copy the example .env file
  cp -v .env.example .env

  # Update the values in your new .env file
  ```

- Build and run the Docker containers:
  ```bash
  inv up --build
  ```
- Access the `app` container's shell:
  ```bash
  inv exec app bash
  ```

Inside the container, you can run the following commands:

- Run tests:
  ```bash
  inv test
  ```
- Generate a new digest:
  ```bash
  inv digest
  ```

See available [invoke](https://www.pyinvoke.org/) tasks with `invoke -l`.

The project uses [pgweb](https://github.com/sosedoff/pgweb) to visualize database changes. Access it at <http://127.0.0.1:8081>.

### Web

This project uses Node.js [v18](https://nodejs.org/en/blog/release/v18.0.0). We recommend using [fnm](https://github.com/Schniz/fnm) or [volta](https://volta.sh/) to manage Node.js versions.

- Install frontend dependencies:
  ```bash
  npm install
  ```
- Start the local development server (accessible at <http://127.0.0.1:8080/>):
  ```bash
  npm start
  ```

See other available scripts in `package.json`.

## Deployment

The project's final output is a **static site**, which can be hosted on any platform that supports static files, such as [Cloudflare Pages](https://pages.cloudflare.com/), [Netlify](https://www.netlify.com/), [Vercel](https://vercel.com/), or [GitHub Pages](https://pages.github.com/).

> **Warning**
>
> Ensure that environment variables are updated accordingly for both the **core** application and the **web** build process.

For an automated, hands-off setup, follow these steps:

1.  Set up a [nix-based](https://en.wikipedia.org/wiki/Unix-like) machine (e.g., a VPS or your laptop) with a Python virtual environment, `docker`, and `docker-compose`.
2.  Configure a cron job to run the `cron.sh` script located in the project root. This script automates the generation and deployment process.
3.  Ensure `git` is configured correctly on the machine, as the `cron.sh` script pushes the generated content to the repository, which in turn triggers the website's build and deployment pipeline.

> **Note**
>
> The `cron.sh` script uses [Apprise](https://github.com/caronc/apprise) to send notifications when a new digest is ready. You will need to configure the notification service (e.g., ntfy.sh) in your `.env` file.

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

- [ ] Improve test coverage

### Frontend (Web)

- [ ] Create a dynamic `og:image` for each digest.
- [ ] Keep things DRY. For example, the header and footer icons.
- [ ] Improve the mobile UI.
- [ ] Improve accessibility (a11y).
- [ ] Implement search functionality for the news digests.

### Features for future releases

- [ ] Add weather reports/forecasts
- [ ] Add exchange rates feature.
- [ ] Consider more sustainable AI integrations
- [ ] Add [Diamond TV](https://diamondtvzambia.com) as a news source.

## Credits

### Music

- <https://pixabay.com/music/beats-sweet-breeze-167504/>
- <https://pixabay.com/music/beats-aesthetic-beat-royalty-free-music-215851/>
- <https://pixabay.com/music/beats-digital-technology-131644/>
- <https://pixabay.com/music/beats-stellar-echoes-202315/>
- <https://pixabay.com/music/afrobeat-it-afrobeat-149308/>

### Icons

- <https://www.pngrepo.com/svg/227923/news-reporter-woman>
- <https://www.svgrepo.com/svg/205960/news-paper>

### News Sources

- [ZNBC](https://znbc.co.zm/)
- [Zambia Daily Mail](http://www.daily-mail.co.zm/)
- [Times of Zambia](https://times.co.zm/)
- [News Diggers!](https://diggers.news/)
- [Muvi TV](https://www.muvitv.com/)
- [Mwebantu](https://www.mwebantu.com/)
