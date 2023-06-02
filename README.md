# zed-news

> automated news podcast

## Credits

- <https://pixabay.com/music/beats-classical-hip-hop-143320/>
- <https://pixabay.com/music/beats-digital-technology-131644/>

## Automated Audio Conversion

Here we assume that the instrumental file is already presentand that it has its **gain** reduced by -20dB.

This can be done as follows:

```bash
ffmpeg -i instrumental.src.mp3 -af "volume=-20dB" instrumental-20dB.mp3
```

### 1. convert the AWS Polly file to mp3

```bash
ffmpeg -i 1652d80b-985d-4ee2-86c6-b8c74620e17a.mpga -c copy 2023-05-24.src.mp3
```

### 2. Convert audio file from mono to 128 kb/s stereo

```bash
ffmpeg -i 2023-05-24.src.mp3 -af "pan=stereo|c0=c0|c1=c0" -b:a 128k 2023-05-24.stereo.mp3
```

### 3. Sound equalization

The sound is too 'muffled', we need to increase the treble frequencies and reduce the bass a little.

Here's an approach, based on <https://stackoverflow.com/questions/39607741/ffmpeg-how-to-reduce-bass-and-increase-treble-like-audacity>

Notes:

- The gain for **0 Hz** should be the _bass_ value you used.
- **250 Hz** gain should be half the bass value.
- **1000 Hz** remains as is - no gain.
- **4000** Hz value should be half the treble value.
- The gain for **16000 Hz** should be the _treble_ value.

```bash
ffmpeg -y -i original.mp3 -af "firequalizer=gain_entry='entry(0,-23);entry(250,-11.5);entry(1000,0);entry(4000,8);entry(16000,16)'" test1.mp3
```

Or we could just simply

```bash
ffmpeg -i input.mp3 -af "treble=g=10" output.mp3
```

The ffmpeg filter `-af "treble=g=10"` adjusts the treble (high-frequency) audio component of the input audio file. The `g=10` parameter specifies the gain in decibels (dB) to be applied to the treble frequencies.

### 4. Mix the voice and instrumental(s)

> We want an intro instrumental and an outro
> We could use the same one, or two separate ones
> Maybe do some manual editing of the sounds so that:
> intro starts at normal volume and then fades to -20dB
> outro starts at low volume and gradually builds up to normal

```bash
# step 0: core
ffmpeg -i 2023-05-24.stereo.mp3 -i instrumental-20dB.mp3 -filter_complex amix=inputs=2:duration=longest:dropout_transition=0:weights="1 0.25":normalize=0 2023-05-24.mixed_by_ffmpeg.mp3

# step 1: get the duration of the mixed file
ffmpeg -i 2023-05-24.mixed_by_ffmpeg.mp3 2>&1 | grep "Duration"

# step 2: pad the instrumental with silence, using duration above and
# the instrumental's duration
# adelay = (duration above - instrumental duration) in milliseconds
ffmpeg -i instrumental-20dB.mp3 2>&1 | grep "Duration"
ffmpeg -i instrumental-20dB.mp3 -af "adelay=484170|484170" ending.mp3

# mix the file from step 0 and step 2
ffmpeg -i 2023-05-24.mixed_by_ffmpeg.mp3 -i ending.mp3 -filter_complex amix=inputs=2:duration=longest:dropout_transition=0:weights="1 0.25":normalize=0 2023-05-24.dist.mp3
```

### 5. Add id3 tags

```bash
eyeD3 -a "Victor Miti" -A "Zed News" -t "Zed News Podcast, Episode 003 (Wednesday 24 May 2023)" -n 3 -Y 2023 2023-05-24.dist.mp3
eyeD3 --genre "Podcast" 2023-05-24.dist.mp3
eyeD3 --add-image album-art.jpg:FRONT_COVER 2023-05-24.dist.mp3
```

## RSS

- <https://rss.com/blog/how-to-create-an-rss-feed-for-a-podcast/>
- <https://riverside.fm/blog/podcast-rss-feed>
- <https://www.podcastinsights.com/podcast-rss-feed/>
- <https://help.spotifyforpodcasters.com/hc/en-us/articles/12515678291995-Your-RSS-feed>
- <https://podcasters.apple.com/support/823-podcast-requirements>
- <https://support.google.com/podcast-publishers/answer/9889544?hl=en>
- <https://castos.com/podcast-rss-feed/>

## TODO

### Tasks

#### High level

- [x] create web app (static site generator)
- [x] register with podcast providers
- [x] deployment

#### Web

- [x] Implement episode listing template (loop through collection)
- [x] Add pagination on listing template
- [x] [Incremental builds](https://11ty.rocks/posts/smart-incremental-rebuilds-with-eleventy-import/)
- [x] Implement RSS. Use <https://podba.se/> to validate
- [x] if user on apple device, add Apple podcasts URL, else, Google podcasts
- [x] Add analytics when not in development
- [ ] Add popup on **Listen and Subscribe button** so that people can choose multiple services
- [ ] Implement search on the web app
- [ ] Dark mode
- [ ] Learn more about [using the aria-current attribute](https://tink.uk/using-the-aria-current-attribute/)

#### Core

- [x] Store retrieved data in a database
- [x] Create data to be passed to 11ty
- [x] write a script to generate a single episode nunjucks file with the correct info, in the correct location
- [x] Delete the Generated file from S3 after downloading it
- [ ] Add a separate module for summarization backends so we can choose which one to work with
- [ ] Add appropriate error handling on `requests` and `feedparser` jobs as well as all other operations, such connecting to AWS Polly, etc.
- [ ] Add task to perform substitution so that, for instance, K400 is written as 400 Kwacha. the AWS Polly voices fail to read Zambian money correctly.

#### Features for future releases

- [ ] Allow for passing of an arg variable for the voice, or dynamically choose a voice from a list, just like the random intros and outros.
- [ ] Mention the weather in Lusaka, Livingstone, Kabwe, etc. Even the weather forecast
- [ ] Mention exchange rates

#### Podcast URLs

- Spotify: <https://open.spotify.com/show/14vv6liB2y2EWgJGRsNWVa>
- Apple: <https://podcasts.apple.com/us/podcast/zed-news-podcast/id1690709989>
- RSS: <{{ site.base_url }}/feed.xml>
- Deezer: <https://deezer.com/show/6126025>
- Google: <>
- PlayerFM: <>
- Tune In: <>
- JioSaavn: <>
- Sticher: <>
- iheartRadio: <>
- PocketCast: <>
- RadioPublic: <>
- Gaana: <>
