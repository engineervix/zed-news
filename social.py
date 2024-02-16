#!/usr/bin/env python

"""social.py

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
import requests
import together
from dotenv import load_dotenv
from moviepy.editor import AudioFileClip, CompositeVideoClip, ImageClip, TextClip, VideoFileClip

from app.core.utilities import ASSETS_DIR, DATA_DIR, configure_logging, today, today_human_readable, today_iso_fmt

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


def create_video(image_overlay, logo, podcast_mp3, video_loop):
    # Load the video clip
    video_clip = VideoFileClip(video_loop)

    # Load the image clip
    image_clip = VideoFileClip(image_overlay)

    # Load the audio clip
    audio_clip = AudioFileClip(podcast_mp3)

    # Load the logo image
    logo_clip = ImageClip(logo, transparent=True)

    # Resize the logo to desired size (optional)
    logo_clip = logo_clip.resize(height=100)  # Resize the logo to a height of 100 pixels while preserving aspect ratio

    # Position the logo at the bottom right corner
    logo_position = (video_clip.size[0] - logo_clip.size[0], video_clip.size[1] - logo_clip.size[1])
    logo_clip = logo_clip.set_position(logo_position)

    # Resize the image to fit within the video dimensions while preserving aspect ratio
    image_clip_resized = image_clip.resize(
        height=video_clip.h
    )  # Resize the image to match the video's height while preserving aspect ratio

    # Loop the video to match the duration of the audio
    looped_video_clip = video_clip.loop(duration=audio_clip.duration)

    # Set opacity and duration for the image clip
    image_clip_resized = (
        image_clip_resized.set_position(("center", "center")).set_duration(looped_video_clip.duration).set_opacity(0.4)
    )  # Adjust opacity as needed (0.0 for fully transparent, 1.0 for fully opaque)

    # Add text overlays
    text_duration = 12  # Duration of the text overlays (in seconds)

    # Text at the beginning
    if episode_number := get_episode_number(news_headlines):
        episode_suffix = f" Episode {episode_number}"
        next_episode = int(episode_number) + 1
        ending_suffix = f" for episode {str(next_episode)}"
        output = f"{DATA_DIR}/{today_iso_fmt}_zed-news-podcast-ep{episode_number}.mp4"
    else:
        episode_suffix = ""
        ending_suffix = ""
        output = f"{DATA_DIR}/{today_iso_fmt}_zed-news-podcast.mp4"

    next_day = determine_next_episode(today)

    text_start = (
        TextClip(
            f"{today_human_readable}\nZed News Podcast{episode_suffix}",
            fontsize=75,
            color="white",
            # to get list of available fonts, use moviepy.video.VideoClip.TextClip.list('font')
            font="Merriweather-Regular",
        )
        .set_duration(text_duration)
        .set_position(("center", "top"))
    )

    # Text at the end
    text_end = (
        TextClip(f"Please join us {next_day}{ending_suffix}!", fontsize=60, color="white", font="Vibur")
        .set_duration(text_duration)
        .set_position(("center", "center"))
    )

    # Overlay the image on top of the looped video
    final_clip = CompositeVideoClip([looped_video_clip.set_opacity(1), image_clip_resized])

    # Overlay the logo on the final clip
    final_clip = CompositeVideoClip(
        [
            final_clip,
            logo_clip.set_opacity(1),
            text_start.set_start(0),
            text_end.set_start(looped_video_clip.duration - text_duration),
        ]
    )

    # Set audio for the final video
    final_clip = final_clip.set_audio(audio_clip)

    # Set the duration of the final clip
    final_clip = final_clip.set_duration(audio_clip.duration)

    # Write the final video to a file
    final_clip.write_videofile(output, codec="libx264", fps=video_clip.fps)

    return output


def create_facebook_post(content: str, url: str) -> str:
    """
    Create a Facebook post using Together AI's Inference API.

    https://docs.together.ai/reference/complete
    """

    prompt = f"You are a social media marketing guru. Your task is to immediately produce a short Facebook teaser post of today's podcast episode whose details are below. Use bullet points, emojis and hashtags as appropriate. Don't cover every news item, just the most interesting ones. Your post will accompany a video, whose URL is {url}. Please note that this video is just basically the audio with some looping animated background, therefore, your post shouldn't ask people to 'watch' the video per se, but rather to, 'check it out' or 'tune in to'. Do not use markdown.\n\n```\n{content}\n```"

    # model = "lmsys/vicuna-13b-v1.5-16k"
    # model = "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO"
    # model = "openchat/openchat-3.5-1210"
    model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
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

    prompt = f"Given the details of today's episode below, write a two-sentence summary to use as a description for the media file.\n\n```\n{content}\n```"

    # model = "lmsys/vicuna-13b-v1.5-16k"
    # model = "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO"
    # model = "openchat/openchat-3.5-1210"
    model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    temperature = 0.7
    max_tokens = 512

    output = together.Complete.create(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    logger.info(output)

    if result := output["output"]["choices"][0]["text"].strip():
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
                # First, we create a video and upload it
                video = create_video(
                    image_overlay=get_random_image(os.path.join(f"{ASSETS_DIR}/images/")),
                    logo=f"{ASSETS_DIR}/logo.png",
                    podcast_mp3=f"{DATA_DIR}/{today_iso_fmt}_podcast_dist.mp3",
                    video_loop=get_random_video(os.path.join(f"{DATA_DIR}/videos/")),
                )
                episode_summary = create_episode_summary(get_content())
                if video_link := upload_video_to_facebook(
                    video,
                    title=f"Zed News Podcast - Episode {get_episode_number(news_headlines)} ({today_human_readable})",
                    description=episode_summary,
                ):
                    # Then we create a facebook post
                    content = get_content()
                    facebook_post = create_facebook_post(content, video_link)
                    post_to_facebook(facebook_post, video_link)
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
