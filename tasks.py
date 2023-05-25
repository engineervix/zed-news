import datetime
import glob
import json
import os
import pathlib
import random
import re
import subprocess

import boto3
import eyed3
import pytz
import requests
from dotenv import load_dotenv
from invoke import task
from langchain import OpenAI, PromptTemplate
from num2words import num2words

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
XI_API_KEY = os.getenv("XI_API_KEY")
llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)


def suffix(d):
    return "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")


def custom_strftime(format, t):
    return t.strftime(format).replace("{S}", str(t.day) + suffix(t.day))


def get_episode_number(initial_date, final_date):
    count = (final_date - initial_date).days + 1
    return count


podcast_host = "Emma"
podcast_start_date = datetime.date(2023, 5, 22)

timezone = pytz.timezone("Africa/Lusaka")
today = datetime.datetime.now(timezone).date()

today_iso_fmt = today.isoformat()
today_human_readable = custom_strftime("%A {S} %B, %Y", today)

episode_number = num2words(get_episode_number(podcast_start_date, today), to="ordinal")


def random_opening():
    data = [
        f"Today is {today_human_readable}. Welcome to the {episode_number} edition of the Zed News Podcast — I'm your friendly host, {podcast_host}, and I'm thrilled to have you join us on this journey of exploring the latest news and stories from across Zambia.",
        f"Today is {today_human_readable}. Welcome to the {episode_number} installment of the Zed News Podcast! I'm {podcast_host}, your amiable host, and I'm excited to have you accompany us as we embark on a voyage through the latest news and stories from across Zambia.",
        f"Greetings and a warm welcome to the {episode_number} edition of the Zed News Podcast! It's {today_human_readable}, and I'm your genial host, {podcast_host}. Join us as we dive into the dynamic world of news and uncover the intriguing narratives shaping Zambia's landscape.",
        f"We're thrilled to have you here on this {today_human_readable}, for the {episode_number} edition of the Zed News Podcast! I'm {podcast_host}, your affable host, and together, let's embark on an enriching journey through the vibrant tapestry of news and stories that define Zambia.",
        f"Welcome, welcome! It's a pleasure to have you join us today for the {episode_number} installment of the Zed News Podcast! I'm {podcast_host}, your friendly guide through the ever-evolving news landscape of Zambia. Get ready to immerse yourself in the latest headlines and captivating narratives that await us.",
        f"Here we are, on {today_human_readable}, marking the {episode_number} edition of the Zed News Podcast! I'm {podcast_host}, your enthusiastic host, and I'm delighted to have you with us as we traverse the vast expanse of news and stories that illuminate the heart of Zambia.",
    ]

    return random.choice(data)


def random_intro():
    data = [
        "Whether you're commuting, relaxing at home, or going about your day, the Zed News Podcast is designed to keep you informed and engaged. We know your time is valuable, so we'll deliver the news in a concise yet captivating format, allowing you to stay updated without feeling overwhelmed.",
        "In today's episode, we'll dive into the headlines making waves across Zambia. Sit back, relax, and let's explore the stories that shape our nation.",
        "As we delve into the news landscape, we'll bring you a curated selection of the most important stories from various sources. Stay tuned for a brief overview of what's happening in Zambia.",
        "Join us on this informative journey as we uncover the latest developments and provide you with a snapshot of the events happening around Zambia and beyond.",
        "Our automated curation process scours the web to compile the most relevant news stories just for you. Get ready for a concise yet comprehensive rundown of the news buzzing in Zambia.",
        "With our advanced algorithms, we've handpicked the top stories that matter. From breaking news to compelling features, we'll keep you up to date with the pulse of Zambia.",
    ]

    return random.choice(data)


def random_dig_in():
    variations = [
        "Without any more delay, let's jump right in.",
        "No time to waste, let's get started.",
        "Let's not wait any longer, it's time to delve in.",
        "Without further ado, let's dive in.",
        "Without prolonging the anticipation, let's begin our exploration.",
        "Time to embark on our news journey. Let's dive right in.",
    ]

    return random.choice(variations)


def random_outro():
    variations = [
        f"And that, dear listeners, brings us to the end of another fantastic edition of the 'Zed News Podcast'. I hope you enjoyed our time together today, catching up on the latest happenings. Until next time, this is {podcast_host} signing off, wishing you a wonderful day or night ahead. Take care, stay safe, and keep being awesome. Later!",
        f"And with that, we come to the conclusion of another captivating edition of the 'Zed News Podcast'. I hope you found our exploration of the news landscape insightful and illuminating. Until we meet again, this is {podcast_host} bidding you farewell, wishing you a remarkable day or night. Stay informed, and keep making a difference. Goodbye, everyone!",
        f"That brings us to the end of this remarkable episode of the 'Zed News Podcast'. I trust you found our discussion enlightening and thought-provoking. Until next time, this is {podcast_host}, your host, signing off. Take care and see ypou later!",
        f"And with that, we wrap up another exciting edition of the 'Zed News Podcast'. I hope you enjoyed our time together, staying up to date with the latest news. Until we reconvene, this is {podcast_host}, your friendly voice in the news, saying farewell. Bye for now!",
        f"That concludes our journey through this edition of the 'Zed News Podcast'. I trust you found our exploration of the news landscape insightful and illuminating. Until our paths cross again, this is {podcast_host}, your guide in the realm of information, bidding you adieu. Bye bye for now!",
        f"And so, we reach the end of another remarkable episode of the 'Zed News Podcast'. I hope you found our analysis and storytelling captivating and informative. Until we meet again, this is {podcast_host}, your companion on the news adventure, signing off. May your day or night be filled with meaningful connections, profound discoveries, and a commitment to positive change. God willing, tizaonana mailo!",
        f"That brings us to the conclusion of this edition of the 'Zed News Podcast'. I hope you enjoyed our exploration of the news landscape and gained valuable insights. Until our paths cross again, this is {podcast_host}, your friendly host, bidding you farewell. Goodbye folks!",
    ]
    return random.choice(variations)


intro = f"""{random_opening()}

{random_intro()}

{random_dig_in()}
"""

outro = random_outro()


@task
def fetch_znbc_news(c):
    c.run("python src/fetch_znbc_news.py", pty=True)


@task
def fetch_other_news(c):
    c.run("python src/fetch_other_news.py", pty=True)


@task
def combine_json_files(c):
    """Combine JSON files"""

    json_files = glob.glob("data/_*.json")
    data = []
    for json_file in json_files:
        with open(json_file) as f:
            data.extend(json.load(f))

    with open(f"data/{today_iso_fmt}_news.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _read_json_file(file):
    with open(file) as f:
        return json.load(f)


@task
def create_podcast_content(c):
    """Create content for the podcast

    Steps:
    0. read data from data/{today_iso_fmt}_news.json
    1. categorize the data by source
    2. write a brief intro welcoming the listener to the podcast
    3. for each source:
        - mention that we're reading from the source
        - for each news item:
            - read the title
            - if item has category, specify that it was posted in that category
            - read the content
    4. write a brief outro thanking the listener for listening to the podcast
    """

    data = _read_json_file(f"data/{today_iso_fmt}_news.json")

    # Create a dictionary to store the articles by source
    articles_by_source = {}

    # Iterate over each article in the data
    for article in data:
        source = article["source"].replace("Zambia National Broadcasting Corporation (ZNBC)", "ZNBC")

        # If the source is not already a key in the dictionary, create a new list
        if source not in articles_by_source:
            articles_by_source[source] = []

        # Add the article to the list for the corresponding source
        articles_by_source[source].append(article)

    read = ""

    for count, source in enumerate(articles_by_source, start=1):
        if count == 1:
            read += "We are going to start with news from "
        elif count == len(articles_by_source):
            read += "To wrap up today's edition, let's check out the news from "
        else:
            read += "Next up, we have news from "

        read += source

        article_count = len(articles_by_source[source])
        if article_count > 9:
            read += (
                f", which has an astounding {article_count} entries today! Let's try and go through them quickly.\n\n"
            )
        else:
            read += f", which has {article_count} entries today.\n\n"

        # Iterate over each article in the source
        for index, article in enumerate(articles_by_source[source], start=1):
            count = num2words(index)
            count_ordinal = num2words(index, to="ordinal")
            count_variations = [
                f"Entry number {count} ",
                f"The {count_ordinal} entry ",
            ]

            title = article["title"]

            content = article["content"]

            template = """
            Please provide a very short, sweet, informative and engaging summary of the following news entry, in not more than two sentences.
            Please provide your output in a manner suitable for reading as part of a podcast.

            {entry}
            """

            prompt = PromptTemplate(input_variables=["entry"], template=template)
            summary_prompt = prompt.format(entry=content)

            num_tokens = llm.get_num_tokens(summary_prompt)
            print(f"'{title}' and its prompt has {num_tokens} tokens")

            summary = llm(summary_prompt)

            category = article["category"] if article["category"] else ""
            read += f"{random.choice(count_variations)} is entitled '{title}' "
            if category:
                read += f"and was posted in the {category} category."
            read += f"\n{summary.strip()}\n\n"

    # Write the intro, the read, and the outro to a file
    with open(f"data/{today_iso_fmt}_podcast-content.txt", "w") as f:
        f.write(intro)
        f.write(read)
        f.write(outro)


def run_ffmpeg_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, _ = process.communicate()
    return output.decode("utf-8")


def extract_duration_in_milliseconds(output):
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


@task
def mix_audio(c, voice_track, intro_track, outro_track, dest=f"data/{today_iso_fmt}_podcast_dist.mp3"):
    """
    Mix the voice track, intro track, and outro track into a single audio file
    """

    voice_track_file_name = os.path.splitext(voice_track)[0]
    voice_track_in_stereo = f"{voice_track_file_name}.stereo.mp3"
    initial_mix = f"{voice_track_file_name}.mix-01.mp3"

    # convert voice track from mono to 128 kb/s stereo
    c.run(
        f'ffmpeg -i {voice_track} -af "pan=stereo|c0=c0|c1=c0" -b:a 128k {voice_track_in_stereo}',
        pty=True,
    )

    # initial mix: the intro + voice track
    c.run(
        f'ffmpeg -i {voice_track_in_stereo} -i {intro_track} -filter_complex amix=inputs=2:duration=longest:dropout_transition=0:weights="1 0.25":normalize=0 {initial_mix}',
        pty=True,
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
        c.run(f'ffmpeg -i {outro_track} -af "adelay={adelay}|{adelay}" {padded_outro}', pty=True)

        # final mix: the initial mix + the padded outro
        c.run(
            f'ffmpeg -i {initial_mix} -i {padded_outro} -filter_complex amix=inputs=2:duration=longest:dropout_transition=0:weights="1 0.25":normalize=0 {dest}',
            pty=True,
        )

        # add Id3 tags
        episode = get_episode_number(podcast_start_date, today)
        audio_file = dest
        tag = eyed3.load(audio_file).tag
        tag.artist = "Victor Miti"
        tag.album = "Zed News"
        tag.title = f"Zed News Podcast, Episode {episode:03} ({today_human_readable})"
        tag.track_num = episode
        tag.release_date = eyed3.core.Date(today.year, today.month, today.day)
        tag.genre = "Podcast"
        tag.save()

        # TODO: Add album art
        # album_art_file = "album-art.jpg"
        # audio = eyed3.load(audio_file)
        # audio.tag.images.set(3, open(album_art_file, "rb").read(), "image/jpeg")
        # audio.tag.save()

        # Clean up
        c.run(f"rm -v {voice_track_in_stereo}")
        c.run(f"rm -v {initial_mix}")
        c.run(f"rm -v {padded_outro}")


@task
def create_audio(c):
    """Create audio from the podcast content

    1. read the podcast content from data/{today_iso_fmt}_podcast-content.txt
    2. send the podcast content to AWS polly for text to speech conversion
    3. download the audio file
    """

    # content = f"data/{today_iso_fmt}_podcast-content.txt"
    content = "data/foo.txt"
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
    response = polly.synthesize_speech(
        Text=podcast_content,
        OutputFormat="mp3",
        VoiceId=podcast_host,
        Engine="standard",
    )

    # Save the MP3 file to disk
    dest = f"data/{today_iso_fmt}"
    pathlib.Path(f"{dest}").mkdir(parents=True, exist_ok=True)
    src_mp3 = f"{dest}/{today_iso_fmt}.src.mp3"
    with open(f"{src_mp3}", "wb") as f:
        f.write(response["AudioStream"].read())

    # pass it on to the mix engineer
    intro_instrumental = "data/intro.mp3"
    outro_instrumental = "data/outro.mp3"
    mix_audio(c, voice_track=src_mp3, intro_track=intro_instrumental, outro_track=outro_instrumental)

    # Cleanup
    znbc_news = f"_znbc_news_{today_iso_fmt}.json"
    other_news = f"_other_news_{today_iso_fmt}.json"
    combined_news = f"{today_iso_fmt}_news.json"

    c.run(f"mv -v {content} {dest}/", pty=True)
    c.run(f"mv -v {znbc_news} {dest}/", pty=True)
    c.run(f"mv -v {other_news} {dest}/", pty=True)
    c.run(f"mv -v {combined_news} {dest}/", pty=True)

    # ----------------------------------------------------
    # If we need to upload a file to S3:
    # We'd first create an S3 client
    # s3 = boto3.client(
    #     "s3",
    #     region_name=AWS_REGION_NAME,
    #     aws_access_key_id=AWS_ACCESS_KEY_ID,
    #     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    # )

    # Then upload to S3
    # s3.upload_file(content, AWS_BUCKET_NAME, os.path.basename(content))
    # ----------------------------------------------------


def toolchain(c):
    """The toolchain for creating the podcast audio"""

    # 1. Download the news
    fetch_other_news(c)
    fetch_znbc_news(c)

    # 2. Combine the news into a single file
    combine_json_files(c)

    # 3. Create the podcast content
    create_podcast_content(c)

    # 3. Create the audio
    create_audio(c)
