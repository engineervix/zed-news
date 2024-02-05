#!/usr/bin/env python

"""social.py

post to social media
"""

__version__ = "0.0.0"

import argparse
import logging
import os
import pathlib
import sys
from http import HTTPStatus

import facebook
import requests
import together
from dotenv import load_dotenv

from app.core.utilities import DATA_DIR, configure_logging, today_iso_fmt

logger = logging.getLogger(__name__)
load_dotenv()

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
HEALTHCHECKS_FACEBOOK_PING_URL = os.getenv("HEALTHCHECKS_FACEBOOK_PING_URL")

# Facebook
# Note: Better to use a Page Access Token (valid for 2 months)
# References:
# - https://medium.com/nerd-for-tech/automate-facebook-posts-with-python-and-facebook-graph-api-858a03d2b142
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
# - https://developers.facebook.com/docs/facebook-login/guides/access-tokens#usertokens
# - https://stackoverflow.com/questions/18664325/how-to-programmatically-post-to-my-own-wall-on-facebook

# Together
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
together.api_key = TOGETHER_API_KEY

news_headlines = f"{DATA_DIR}/{today_iso_fmt}_news_headlines.txt"
podcast_url = f"https://zednews.pages.dev/episode/{today_iso_fmt}/"


def setup():
    configure_logging()

    # cd to the PROJECT_ROOT
    os.chdir(PROJECT_ROOT)


def podcast_is_live(url):
    """Check if the podcast is live"""
    try:
        response = requests.head(url)
        return response.status_code != HTTPStatus.NOT_FOUND
    except requests.exceptions.RequestException:
        return False


def get_content() -> str:
    """Get the headlines"""
    with open(news_headlines, "r") as f:
        return f.read()


def create_facebook_post(content: str) -> str:
    """
    Create a Facebook post using Together AI's Inference API.

    https://docs.together.ai/reference/complete
    """

    prompt = f"You are a social media marketing guru. Your task is to produce a short facebook teaser post of today's podcast whose details are below. Use bullet points, emojis and hashtags as appropriate. Don't cover every news item, just the most interesting ones.```{content}\n```"

    # model = "lmsys/vicuna-13b-v1.5-16k"
    # model = "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO"
    model = "openchat/openchat-3.5-1210"
    temperature = 0.75
    max_tokens = 1024

    output = together.Complete.create(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    logger.info(output)

    if result := output["output"]["choices"][0]["text"].strip():
        return result
    else:
        logger.error("Transcript is empty")
        requests.get(f"{HEALTHCHECKS_FACEBOOK_PING_URL}/fail", timeout=10)
        sys.exit(1)


def post_to_facebook(content: str, url: str) -> None:
    """Post a link to the Facebook page"""
    graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN)
    graph.put_object(
        parent_object=FACEBOOK_PAGE_ID,
        connection_name="feed",
        message=content,
        link=url,
    )
    logger.info(url)
    logger.info(content)


def main(args=None):
    """Console script entry point"""

    if not args:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="social.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.version = __version__
    parser.add_argument("-v", "--version", action="version")

    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # share parser
    share_parser = subparsers.add_parser("share", help="Share to a specific platform")
    share_parser.add_argument(
        "platform",
        choices=["facebook"],
        help="Which platform to share to. Currently only Facebook is supported.",
        type=str,
    )

    # add other parsers here as you please
    # subparsers.add_parser("foo", help="...")

    args = parser.parse_args(args)

    if args.command == "share":
        if args.platform == "facebook" and podcast_is_live(podcast_url):
            try:
                content = get_content()
                facebook_post = create_facebook_post(content)
                post_to_facebook(facebook_post, podcast_url)
                requests.get(HEALTHCHECKS_FACEBOOK_PING_URL, timeout=10)
            except Exception as e:
                logger.error(e)
                requests.get(f"{HEALTHCHECKS_FACEBOOK_PING_URL}/fail", timeout=10)
        else:
            print("Either the podcast is not live or the platform you specified is not supported.")
            sys.exit(1)
    else:
        print("Please specify a valid command.")
        sys.exit(1)


if __name__ == "__main__":
    setup()
    main()
