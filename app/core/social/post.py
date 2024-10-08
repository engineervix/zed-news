#!/usr/bin/env python

"""post.py

post to social media
"""

__version__ = "0.0.0"

import argparse
import logging
import os
import pathlib
import random
import sys
from http import HTTPStatus

import facebook
import numpy as np
import PIL
import requests
from dotenv import load_dotenv
from moviepy.editor import CompositeVideoClip, ImageClip, TextClip, VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.tools.segmenting import findObjects
from together import Together

from app.core.utilities import (
    ASSETS_DIR,  # noqa: F401
    DATA_DIR,
    configure_logging,
    podcast_host,
    today,
    today_human_readable,
    today_iso_fmt,
)

PROJECT_ROOT = pathlib.Path(__file__).parents[3]

logger = logging.getLogger(__name__)
load_dotenv(dotenv_path=f"{PROJECT_ROOT}/.env")

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
client = Together(api_key=TOGETHER_API_KEY)

news_headlines = f"{DATA_DIR}/{today_iso_fmt}_news_headlines.txt"
transcript = f"{DATA_DIR}/{today_iso_fmt}/{today_iso_fmt}_podcast-content.txt"
podcast_url = f"https://zednews.pages.dev/episode/{today_iso_fmt}/"

# https://stackoverflow.com/questions/76616042/attributeerror-module-pil-image-has-no-attribute-antialias
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS


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
    """Get the podcast content"""
    with open(transcript, "r") as f:
        return f.read()


def get_episode_number(file_path):
    with open(file_path, "r") as file:
        first_line = file.readline().strip()  # Read the first line and remove leading/trailing whitespace
        if first_line.startswith("Title:"):
            title_parts = first_line.split()
            last_word = title_parts[-1]
            if last_word.isdigit():
                return last_word
    return ""


def determine_next_episode(today_date):
    # Determine the day of the week (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
    day_of_week = today_date.weekday()

    # Determine the value of "next"
    if day_of_week < 4:  # Monday to Thursday
        next_episode = "tomorrow"
    else:  # Friday
        next_episode = "on Monday"

    return next_episode


def get_random_video(path):
    """Get a random video from a directory"""
    video_files = [
        f
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.endswith((".mp4", ".avi", ".mkv", ".mov"))
    ]
    if video_files:
        return os.path.join(path, random.choice(video_files))
    else:
        return None


def get_random_image(path):
    """Get a random image from a directory"""
    image_files = [
        f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith((".jpg", ".png"))
    ]
    if image_files:
        return os.path.join(path, random.choice(image_files))
    else:
        return None


def create_video(source_video, logo):
    # Load the video clip
    video_clip = VideoFileClip(source_video)

    width, height = video_clip.size
    screensize = (width, height)

    # Load the logo image
    logo_clip = ImageClip(logo, transparent=True)

    # Resize the logo to desired size (optional)
    logo_clip = logo_clip.resize(height=100)  # Resize the logo to a height of 100 pixels while preserving aspect ratio

    # Position the logo at the bottom right corner
    logo_position = (
        video_clip.size[0] - logo_clip.size[0],
        video_clip.size[1] - logo_clip.size[1],
    )
    logo_clip = logo_clip.set_position(logo_position)

    # the fancy text animation is from
    # https://moviepy-tburrows13.readthedocs.io/en/improve-docs/examples/moving_letters.html

    # helper function
    rotMatrix = lambda a: np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])  # noqa: E731

    def vortex(screenpos, i, nletters):  # noqa: D103
        d = lambda t: 1.0 / (0.3 + t**8)  # damping # noqa: E731
        a = i * np.pi / nletters  # angle of the movement
        v = rotMatrix(a).dot([-1, 0])
        if i % 2:
            v[1] = -v[1]
        return lambda t: screenpos + 400 * d(t) * rotMatrix(0.5 * d(t) * a).dot(v)

    def vortexout(screenpos, i, nletters):  # noqa: D103
        d = lambda t: max(0, t)  # damping # noqa: E731
        a = i * np.pi / nletters  # angle of the movement
        v = rotMatrix(a).dot([-1, 0])
        if i % 2:
            v[1] = -v[1]
        return lambda t: screenpos + 400 * d(t - 0.1 * i) * rotMatrix(-0.2 * d(t) * a).dot(v)

    # Add text overlays
    text_duration = 12  # Duration of the text overlays (in seconds)

    # Text at the beginning
    if episode_number := get_episode_number(news_headlines):
        episode_suffix = f" Episode {episode_number}"
        next_episode = int(episode_number) + 1
        ending_suffix = f" for episode {str(next_episode)}"
        output = f"{DATA_DIR}/{today_iso_fmt}_zed-news-podcast-ep{episode_number}.mp4"
    else:
        # episode_suffix = ""
        episode_suffix = "Welcome!"
        ending_suffix = ""
        output = f"{DATA_DIR}/{today_iso_fmt}_zed-news-podcast.mp4"

    next_day = determine_next_episode(today)

    text_start = (
        TextClip(
            # f"{today_human_readable}\nZed News Podcast{episode_suffix}",
            f"{episode_suffix.strip()}",
            fontsize=120,
            kerning=5,
            color="white",
            # to get list of available fonts, use moviepy.video.VideoClip.TextClip.list('font')
            font="Cookie-Regular",
        )
        # .set_duration(text_duration)
        # .set_position(("center", "top"))
    )

    # Text at the end
    text_end = (
        TextClip(
            f"Please join us {next_day}{ending_suffix}!",
            fontsize=80,
            size=screensize,
            method="caption",
            kerning=5,
            color="white",
            font="Cookie-Regular",
        )
        .set_duration(text_duration)
        .set_position(("center", "center"))
    )

    letters = findObjects(CompositeVideoClip([text_start.set_position("center", "center")], size=screensize))

    def moveLetters(letters, funcpos):  # noqa D103
        return [letter.set_pos(funcpos(letter.screenpos, i, len(letters))) for i, letter in enumerate(letters)]

    clips = [
        CompositeVideoClip(moveLetters(letters, funcpos), size=screensize).subclip(0, 5)
        for funcpos in [vortex, vortexout]
    ]
    text_clip = concatenate_videoclips(clips)

    final_clip = CompositeVideoClip(
        [
            video_clip.set_opacity(1),
            text_clip,
            logo_clip.set_opacity(1),
            # text_start.set_start(0),
            text_end.set_start(video_clip.duration - text_duration),
        ]
    )

    # Set the duration of the final clip
    final_clip = final_clip.set_duration(video_clip.duration)

    # Write the final video to a file
    final_clip.write_videofile(output, codec="libx264", fps=video_clip.fps)

    return output


def create_facebook_post(content: str, url: str) -> str:
    """
    Create a Facebook post using Together AI's Inference API.

    https://docs.together.ai/reference/complete
    """

    system_prompt = f"You are a social media marketing expert. Your task is to produce a short Facebook teaser post for today's podcast episode based on the provided podcast episode details. The post should highlight only the most interesting news items, using bullet points, emojis, and hashtags where appropriate. Keep in mind that your post will accompany a video, whose URL is {url}, and which is primarily an audio recording with a looping animated background. Therefore, avoid asking people to 'watch' the video. Instead, encourage them to 'check it out' or 'tune in.'"

    user_prompt = f"Produce a Facebook teaser post based on the following podcast episode details.\n\n\n{content}\n"

    model = "meta-llama/Meta-Llama-3-70B-Instruct-Turbo"
    temperature = 0.75
    max_tokens = 1024

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    logger.info(completion)

    if result := completion.choices[0].message.content.strip():
        result = result.replace("```", "")  # Remove triple backticks
        first_line = result.splitlines()[0].lower()
        unwanted = ["facebook post:", "post:", "here's your", "here is"]

        if any(string in first_line for string in unwanted):
            # Remove the first line from result
            result = "\n".join(result.split("\n")[1:])

        return result
    else:
        logger.error("Transcript is empty")
        requests.get(f"{HEALTHCHECKS_FACEBOOK_PING_URL}/fail", timeout=10)
        sys.exit(1)


def create_episode_summary(content: str) -> str:
    """
    Using Together AI's Inference API, create a summary to use as
    the Facebook video description.


    https://docs.together.ai/reference/complete
    """

    title = f"Title: Zed News Podcast episode {get_episode_number(news_headlines)}"
    date = f"Date: {today_human_readable}"
    host = f"Host: {podcast_host}"
    separator = "------------------------------------"

    system_prompt = f"You are a social media marketing guru. Your task is to write a very brief summary to use as a description for a Facebook video post, given the transcript of today's episode below. Use bullet points, emojis, and hashtags as appropriate. Do not use markdown. Please note that this video is just basically the audio with some looping animated background, so your post shouldn't ask people to 'watch' the video, but rather to 'check it out' or 'tune in to'. At the end, mention that more details can be obtained from {podcast_url}."

    user_prompt = f"{separator}\n\n{title}\n{date}\n{host}\n\n{separator}\n\n{content}\n"

    model = "meta-llama/Meta-Llama-3-70B-Instruct-Turbo"
    temperature = 0.75
    max_tokens = 1024

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    logger.info(completion)

    if result := completion.choices[0].message.content.strip():
        result = result.replace("```", "")  # Remove triple backticks
        first_line = result.splitlines()[0].lower()
        unwanted = ["summary:", "here's", "here is", "sure"]

        if any(string in first_line for string in unwanted):
            # Remove the first line from result
            result = "\n".join(result.split("\n")[1:])

        return result
    else:
        logger.error("Podcast episode summary is empty")
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


def upload_video_to_facebook(video_file, title=None, description=None):
    # Step 1: Upload video
    with open(video_file, "rb") as f:
        endpoint = f"https://graph-video.facebook.com/v19.0/me/videos?access_token={FACEBOOK_ACCESS_TOKEN}"

        files = {"file": f}

        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description

        response = requests.post(
            endpoint,
            files=files,
            data=data,
        )
        video_data = response.json()

        if "id" in video_data:
            video_id = video_data["id"]
            print("Video uploaded successfully with ID:", video_id)

            # # Step 2 (optional, because when you upload a video it's added automatically to timeline):
            # Share the video on your Facebook timeline
            # graph_endpoint = "https://graph.facebook.com/v19.0/me/feed"
            # params = {
            #     "access_token": FACEBOOK_ACCESS_TOKEN,
            #     "message": "Check out this video!",
            #     "link": f"https://www.facebook.com/watch/?v={video_id}",
            # }
            # response = requests.post(graph_endpoint, params=params)

            # if response.status_code == 200:
            #     print("Video shared on your Facebook timeline successfully!")
            # else:
            #     print("Failed to share the video on your Facebook timeline.")

            return f"https://www.facebook.com/watch/?v={video_id}"
        else:
            print("Failed to upload the video.")
            return ""


def main(args=None):
    """Console script entry point"""

    if not args:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="post.py",
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
                # First, we create a video and upload it
                video = create_video(
                    source_video=f"{DATA_DIR}/video_{today_iso_fmt}.mp4",
                    logo=f"{ASSETS_DIR}/logo.png",
                )
                episode_summary = create_episode_summary(get_content())
                if video_link := upload_video_to_facebook(
                    video,
                    title=f"Zed News Podcast - Episode {get_episode_number(news_headlines)} ({today_human_readable})",
                    description=episode_summary,
                ):
                    # Then we create a facebook post
                    # content = get_content()
                    # facebook_post = create_facebook_post(content, video_link)
                    # post_to_facebook(facebook_post, video_link)
                    # NOTE: we actually don't need to create a facebook post because
                    # when we upload the video, a post is automatically created
                    print(f"Video successfully uploaded to Facebook. Here's the link: {video_link}")
                    requests.get(HEALTHCHECKS_FACEBOOK_PING_URL, timeout=10)
                else:
                    print(
                        "Something went wrong either while creating the video or attempting to upload it to Facebook."
                    )
                    sys.exit(1)
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
