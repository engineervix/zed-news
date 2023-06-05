import datetime
import logging
import os
import re
import subprocess

import boto3
import eyed3
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import FilePath

from app.core.db.models import MP3
from app.core.podcast.content import get_episode_number
from app.core.utilities import (
    AWS_ACCESS_KEY_ID,
    AWS_BUCKET_NAME,
    AWS_REGION_NAME,
    AWS_SECRET_ACCESS_KEY,
    DATA_DIR,
    IMAGE_DIR,
    delete_file,
    today,
    today_human_readable,
    today_iso_fmt,
)


def run_ffmpeg_command(command: str) -> str:
    """Run an ffmpeg command and return the output"""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, _ = process.communicate()
    return output.decode("utf-8")


def extract_duration_in_milliseconds(output: str) -> int:
    """Extract the duration in milliseconds from the ffmpeg output"""
    duration_pattern = r"Duration:\s+(\d{2}:\d{2}:\d{2}\.\d{2})"
    duration_match = re.search(duration_pattern, output)
    if duration_match:
        duration_str = duration_match.group(1)
        duration_obj = datetime.datetime.strptime(duration_str, "%H:%M:%S.%f")
        duration_in_ms = (
            duration_obj.hour * 3600 + duration_obj.minute * 60 + duration_obj.second
        ) * 1000 + duration_obj.microsecond // 1000
        return duration_in_ms
    else:
        return 0


async def mix_audio(voice_track, intro_track, outro_track, dest=f"{DATA_DIR}/{today_iso_fmt}_podcast_dist.mp3"):
    """
    Mix the voice track, intro track, and outro track into a single audio file
    """

    voice_track_file_name = os.path.splitext(voice_track)[0]
    mix_44100 = f"{voice_track_file_name}.44.1kHz.mp3"
    voice_track_in_stereo = f"{voice_track_file_name}.stereo.mp3"
    eq_mix = f"{voice_track_file_name}.eq-mix.mp3"
    initial_mix = f"{voice_track_file_name}.mix-01.mp3"

    # change the voice track sample rate to 44.1 kHz
    subprocess.run(
        f"ffmpeg -i {voice_track} -ar 44100 {mix_44100}",
        shell=True,
    )

    # convert voice track from mono to 128 kb/s stereo
    subprocess.run(
        f'ffmpeg -i {mix_44100} -af "pan=stereo|c0=c0|c1=c0" -b:a 128k {voice_track_in_stereo}',
        shell=True,
    )

    # adjust the treble (high-frequency).
    # The g=3 parameter specifies the gain in decibels (dB) to be applied to the treble frequencies.
    subprocess.run(
        f'ffmpeg -i {voice_track_in_stereo} -af "treble=g=3" {eq_mix}',
        shell=True,
    )

    # initial mix: the intro + voice track
    subprocess.run(
        f'ffmpeg -i {eq_mix} -i {intro_track} -filter_complex amix=inputs=2:duration=longest:dropout_transition=0:weights="1 0.25":normalize=0 {initial_mix}',
        shell=True,
    )

    # get duration of the initial mix
    command_1 = f'ffmpeg -i {initial_mix} 2>&1 | grep "Duration"'
    output_1 = run_ffmpeg_command(command_1)
    duration_1 = extract_duration_in_milliseconds(output_1)

    command_2 = f'ffmpeg -i {outro_track} 2>&1 | grep "Duration"'
    output_2 = run_ffmpeg_command(command_2)
    duration_2 = extract_duration_in_milliseconds(output_2)

    # pad the outro instrumental with silence, using initial mix duration and
    # the outro instrumental's duration
    # adelay = (duration of initial mix - outro instrumental duration) in milliseconds
    if duration_1 != 0 and duration_2 != 0:
        padded_outro = f"{voice_track_file_name}.mix-02.mp3"

        adelay = duration_1 - duration_2
        subprocess.run(f'ffmpeg -i {outro_track} -af "adelay={adelay}|{adelay}" {padded_outro}', shell=True)

        # final mix: the initial mix + the padded outro
        subprocess.run(
            f'ffmpeg -i {initial_mix} -i {padded_outro} -filter_complex amix=inputs=2:duration=longest:dropout_transition=0:weights="1 0.25":normalize=0 {dest}',
            shell=True,
        )

        # add Id3 tags
        episode = await get_episode_number()
        audio_file = dest
        tag = eyed3.load(audio_file).tag
        tag.artist = "Victor Miti"
        tag.album = "Zed News"
        tag.title = f"Zed News Podcast, Episode {episode:03} ({today_human_readable})"
        tag.track_num = episode
        tag.release_date = eyed3.core.Date(today.year, today.month, today.day)
        tag.genre = "Podcast"
        album_art_file = f"{IMAGE_DIR}/album-art.jpg"
        with open(album_art_file, "rb") as cover_art:
            # The value 3 indicates that the front cover shall be set
            # # https://eyed3.readthedocs.io/en/latest/eyed3.id3.html#eyed3.id3.frames.ImageFrame
            tag.images.set(3, cover_art.read(), "image/jpeg")
        tag.save()

        # Clean up
        for f in [voice_track_in_stereo, mix_44100, eq_mix, initial_mix, padded_outro]:
            delete_file(f)


def upload_to_s3(src: FilePath, dest_folder: str, dest_filename: str):
    """Upload the MP3 file to S3 and return the URL"""

    try:
        s3 = boto3.client(
            "s3",
            region_name=AWS_REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

        # Upload the MP3 file to S3
        dest_key = f"{dest_folder}/{dest_filename}"
        s3.upload_file(src, AWS_BUCKET_NAME, dest_key)

        # Get the URL of the uploaded file
        url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/{dest_key}"

        return url
    except (BotoCoreError, ClientError) as e:
        error_message = f"Error occurred during S3 upload: {str(e)}"
        logging.error(error_message)
        return ""


def get_mp3_info(mp3_file: FilePath) -> dict:
    """Get the filesize and duration of an MP3 file"""
    audiofile = eyed3.load(mp3_file)
    return {"filesize": audiofile.info.size_bytes, "duration": audiofile.info.time_secs}


async def add_to_db(url: str, f: FilePath):
    """Create an mp3 podcast entry in the database"""

    logging.info(f"Adding MP3 {f} to database ...")
    mp3_info = get_mp3_info(f)
    await MP3.create(url=url, **mp3_info)
