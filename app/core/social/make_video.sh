#!/usr/bin/env bash

# =================================================================================================
# description:  Create a video using an image with transparent background, a video and audio file
# author:       Victor Miti <https://github.com/engineervix>
# license:      BSD-3-Clause
#
#
# =================================================================================================

# Exit immediately if any command fails
set -e

# 1. cd to data directory
cd "${HOME}/SITES/tools/zed-news/data" || { echo "Failed to change directory."; exit 1; }

# Source the .env file so we can retrieve healthchecks.io ping URL
# shellcheck source=/dev/null
source ../.env

# Function to send success signal to healthchecks.io
function send_healthcheck_success() {
		curl -fsS --retry 3 "${HEALTHCHECKS_PING_URL}" > /dev/null
}

# Function to send failure signal to healthchecks.io
function send_healthcheck_failure() {
		curl -fsS --retry 3 "${HEALTHCHECKS_PING_URL}/fail" > /dev/null
}

# shellcheck source=/dev/null
source "${HOME}/Env/zed-news/bin/activate" || { echo "Failed to activate virtual environment."; send_healthcheck_failure; exit 1; }

START_TIME=$(date +%s)
DAY_OF_MONTH=$(date +"%d")

live_audio_file="$(date --iso)_podcast_dist.mp3"
source_image="images/ayanda/no-bg/${DAY_OF_MONTH}.png"
source_video="videos/longer-background-videos/$(date '+%A' | tr '[:upper:]' '[:lower:]').mp4"

# Get the duration of the audio file
audio_duration=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "${live_audio_file}")

# Process the video and audio
ffmpeg \
    -i "${source_video}" \
    -i "${source_image}" \
    -i "${live_audio_file}" \
    -filter_complex \
        "[1:v]scale=-1:1080[img]; \
         [0:v][img]overlay,trim=duration=$audio_duration,setpts=PTS-STARTPTS[v]; \
         [2:a]aformat=channel_layouts=stereo,atrim=duration=$audio_duration,asetpts=PTS-STARTPTS[a]" \
    -map "[v]" \
    -map "[a]" \
    -vcodec libx264 \
    -acodec aac \
    -strict experimental \
    "video_$(date --iso).mp4"

# post the video to social platform
cd "${HOME}/SITES/tools/zed-news/" || { echo "Failed to change directory."; exit 1; }
invoke facebook-post

# cleanup
rm -fv "video_$(date --iso).mp4"

END_TIME=$(date +%s)
DURATION=$(( END_TIME - START_TIME ))
echo "Process completed in $DURATION seconds."
send_healthcheck_success
