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
import subprocess
import sys
import tempfile
from http import HTTPStatus

import facebook
import requests
from dotenv import load_dotenv
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
    """Create video using ffmpeg"""

    # Get episode number
    try:
        episode_number = get_episode_number()
        episode_suffix = f"Episode {episode_number}"
        next_episode = int(episode_number) + 1
        ending_suffix = f"for episode {str(next_episode)}"
        output = f"{DATA_DIR}/{today_iso_fmt}_zed-news-podcast-ep{episode_number}.mp4"
    except Exception as e:
        logger.warning(f"Could not get episode number: {e}")
        episode_suffix = "Welcome!"
        ending_suffix = ""
        output = f"{DATA_DIR}/{today_iso_fmt}_zed-news-podcast.mp4"

    # Determine next episode day
    next_day = determine_next_episode(today)

    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create text for intro
        intro_text = episode_suffix.strip()
        intro_file = os.path.join(temp_dir, "intro_text.txt")
        with open(intro_file, "w") as f:
            f.write(intro_text)

        # Create text for outro - split into two lines
        outro_line1 = f"Please join us {next_day}"
        outro_line2 = f"{ending_suffix}!"
        outro_file1 = os.path.join(temp_dir, "outro_text1.txt")
        outro_file2 = os.path.join(temp_dir, "outro_text2.txt")
        with open(outro_file1, "w") as f:
            f.write(outro_line1)
        with open(outro_file2, "w") as f:
            f.write(outro_line2)

        # Get video duration
        ffprobe_cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            source_video,
        ]

        video_duration = float(subprocess.check_output(ffprobe_cmd).decode().strip())

        # Create video with intro animation, logo overlay, and outro text
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            source_video,
            "-i",
            logo,
            "-filter_complex",
            f"""
            [0:v]split=3[bg1][bg2][bg3];

            [bg1]trim=0:5,setpts=PTS-STARTPTS[bg_intro];
            [bg_intro]drawtext=fontfile='{ASSETS_DIR}/Cookie-Regular.ttf':textfile='{intro_file}':fontsize=120:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,5)':alpha='if(lt(t,1),t,if(lt(t,4),1,5-t))':box=0[intro];

            [bg2]trim=0:{video_duration - 5},setpts=PTS-STARTPTS[bg_main];
            [bg_main][1:v]overlay=x=W-w:y=H-h[main];

            [bg3]trim={video_duration - 5}:{video_duration},setpts=PTS-STARTPTS[bg_outro];
            [bg_outro]drawtext=fontfile='{ASSETS_DIR}/Cookie-Regular.ttf':textfile='{outro_file1}':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-40:box=0,
            drawtext=fontfile='{ASSETS_DIR}/Cookie-Regular.ttf':textfile='{outro_file2}':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+40:box=0[outro];

            [intro][main][outro]concat=n=3:v=1:a=0[outv];
            [0:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[outa]
            """,
            "-map",
            "[outv]",
            "-map",
            "[outa]",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-strict",
            "experimental",
            output,
        ]

        # Execute ffmpeg command
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            logger.info(f"Video successfully created at {output}")
            return output
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating video: {e}")
            requests.get(f"{HEALTHCHECKS_FACEBOOK_PING_URL}/fail", timeout=10)
            sys.exit(1)


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
