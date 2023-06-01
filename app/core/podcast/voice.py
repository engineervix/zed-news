import logging
import pathlib
import time

import boto3
from pydantic import FilePath

from app.core.utilities import (
    AWS_ACCESS_KEY_ID,
    AWS_BUCKET_NAME,
    AWS_REGION_NAME,
    AWS_SECRET_ACCESS_KEY,
    DATA_DIR,
    engine,
    lingo,
    podcast_host,
    today_iso_fmt,
)


def create_audio(transcript: FilePath, podcast_host: str = podcast_host, lingo: str = lingo):
    """Create audio from the podcast transcript,
    with the specified podcast host voice and lingo (language code).

    Steps:
    1. read the podcast content from transcript file
    2. send the podcast content to AWS polly for text to speech conversion
    3. download the audio file
    """

    content = transcript
    with open(content, "r") as f:
        podcast_content = f.read()

    # Create a Polly client
    polly = boto3.client(
        "polly",
        region_name=AWS_REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    # Synthesize the text into an MP3 file
    logging.info("Creating an AWS Polly Task ...")
    s3_podcast_dir = "zed-news"
    response = polly.start_speech_synthesis_task(
        Engine=engine,
        LanguageCode=lingo,
        VoiceId=podcast_host,
        Text=podcast_content,
        OutputS3BucketName=AWS_BUCKET_NAME,
        OutputS3KeyPrefix=f"{s3_podcast_dir}/{today_iso_fmt}-raw",
        OutputFormat="mp3",
    )

    # Download the MP3 file from S3
    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    dest = f"{DATA_DIR}/{today_iso_fmt}"
    pathlib.Path(f"{dest}").mkdir(parents=True, exist_ok=True)
    src_mp3 = f"{dest}/{today_iso_fmt}.src.mp3"

    # Check if the task is complete, then download the file
    while True:
        logging.info("Checking if Polly Task is completed...")
        result = polly.get_speech_synthesis_task(TaskId=response["SynthesisTask"]["TaskId"])
        if result["SynthesisTask"]["TaskStatus"] == "completed":
            logging.info("Woohoo! Task completed!")
            break
        time.sleep(5)

    output_key = f"{s3_podcast_dir}/{response['SynthesisTask']['OutputUri'].split('/')[-1]}"
    logging.info("Downloading the MP3 file from S3 ...")
    logging.info(output_key)
    s3.download_file(AWS_BUCKET_NAME, output_key, f"{src_mp3}")

    return output_key


def delete_source_mp3(output_key: str):
    """Delete the AWS Polly generated MP3 file from S3"""

    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    # Delete the original MP3 file from S3
    s3.delete_object(Bucket=AWS_BUCKET_NAME, Key=output_key)
