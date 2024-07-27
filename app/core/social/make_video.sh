#!/usr/bin/env bash

# =================================================================================================
# description:  provision a GPU instance on vast.ai and run [SadTalker](https://github.com/OpenTalker/SadTalker)
# author:       Victor Miti <https://github.com/engineervix>
# license:      BSD-3-Clause
#
# Prerequisites
# -------------
# - You need a vast.ai account (with sufficient credit)
# - Ensure that the `vastai` CLI is installed and configured (https://cloud.vast.ai/cli/)
#
# Steps
# ------
# 1.  Search for available instances based on specified criteria
# 2.  Pick the 1st instance from the results, and launch it
# 3.  copy the files you'll be working with to the remote server
# 4.  setup SadTalker on the remote server
# 5.  run SadTalker
# 6.  copy generated file to host machine
# 7.  destroy GPU instance
# 8.  edit the video with ffmpeg
# 9.  upload the video to relevant channels
# 10. cleanup
# =================================================================================================

# Exit immediately if any command fails
set -e

# 1. cd to data directory
cd "${HOME}/SITES/zed-news/data" || { echo "Failed to change directory."; exit 1; }

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

LOG_FILE="vastai_error_log_$(date +"%Y%m%d_%H%M%S").txt"
START_TIME=$(date +%s)
DAY_OF_MONTH=$(date +"%d")
KEY_NAME="vast_$(date --iso)"
PASSPHRASE=""

live_audio_file="$(date --iso)_podcast_dist.mp3"
source_image="images/ayanda/${DAY_OF_MONTH}.png"
source_audio="$(date --iso)/$(date --iso).src.mp3"

# Search for available instances based on specified criteria
# vastai search offers -d 'num_gpus=1 disk_space>=40 gpu_ram>=40 gpu_arch=nvidia dph<1 dlperf>100' -o 'dph'
# vastai search offers -d 'num_gpus=1 disk_space>=40 gpu_ram>=40 gpu_arch=nvidia dph<1 dlperf>100' -o 'dph' | sed -n '2p' | cut -d ' ' -f 1
# Pick the 1st instance from the results, and launch it
machine_id=$(vastai search offers -d 'num_gpus=1 disk_space>=40 gpu_ram>=40 gpu_arch=nvidia dph<1 dlperf>100' -o 'dph' | sed -n '2p' | cut -d ' ' -f 1)
echo "The ID of the first result is: $machine_id"

# pytorch/pytorch:1.12.1-cuda11.3-cudnn8-devel
# pytorch/pytorch:2.4.0-cuda11.8-cudnn9-devel
vastai create instance "$machine_id" --image pytorch/pytorch:2.4.0-cuda11.8-cudnn9-devel --env '-e TZ=Africa/Lusaka -h sadtalker' --disk 40 --ssh --direct

instance_id=$(vastai show instances | sed -n '2p' | cut -d ' ' -f 1)

get_status() {
		vastai show instance "$instance_id" | awk 'NR==2 {print $3}'
}

handle_vastai_error() {
		echo "An error occurred. Check the log file for details: $LOG_FILE"
		vastai destroy instance "$instance_id"
		END_TIME=$(date +%s)
		DURATION=$(( END_TIME - START_TIME ))
		echo "Script failed after $DURATION seconds."
		send_healthcheck_failure
		exit 1
}

instance_status=$(get_status)
elapsed_time=0
max_time=300  # 5 minutes in seconds

# Check the status every 5 seconds until it is "running" or until the timeout is reached
while [ "$instance_status" != "running" ] && [ $elapsed_time -lt $max_time ]; do
    echo "Current status: $instance_status. Waiting for 'running' status..."
    sleep 5
    elapsed_time=$((elapsed_time + 5))
    instance_status=$(get_status)
done

# if status is "running", let's SSH into the instance
if [ "$instance_status" == "running" ]; then
    echo "Instance is now running!"
    #  We need to generate an SSH key and add it to the machine
    ssh-keygen -t rsa -b 4096 -f "$KEY_NAME" -N "$PASSPHRASE" -C "vast-box-$(date --iso)@$(hostname)"

    vastai attach ssh "$instance_id" "$(cat "$KEY_NAME.pub")"
    # delete last entry in known_hosts
    cp -v ~/.ssh/known_hosts ~/.ssh/known_hosts_"$(date +'%Y%m%d_%H%M%S').bak"
    sed -i '$ d' ~/.ssh/known_hosts
    # disable tmux
    ssh "$(vastai ssh-url "$instance_id")" -o StrictHostKeyChecking=no -i "$KEY_NAME" "touch ~/.no_auto_tmux"
else
    echo "Timeout reached. Instance did not change to 'running' within 5 minutes."
    exit 1
fi

# then copy the audio file and the image to the remote instance
ssh_url=$(vastai ssh-url "$instance_id")
port=$(echo "$ssh_url" | cut -d ':' -f 3)
rsync -chavzP -e "ssh -o StrictHostKeyChecking=no -p $port -i $KEY_NAME" "$source_audio" "$(basename "$ssh_url" | cut -d ':' -f 1)":~/audio.mp3
rsync -chavzP -e "ssh -o StrictHostKeyChecking=no -p $port -i $KEY_NAME" "$source_image" "$(basename "$ssh_url" | cut -d ':' -f 1)":~/image.png

# now you can login and do your thing on the GPU instance
{
	# shellcheck disable=SC2087
	ssh "$(vastai ssh-url "$instance_id")" -o StrictHostKeyChecking=no -i "$KEY_NAME" << EOF
		# Exit immediately if a command exits with a non-zero status
		set -e
		# Redirect stderr to a log file
		exec 2> >(tee -a $LOG_FILE >&2)

		# Update package lists and install necessary packages
		apt-get update && apt-get install libgl1 -y

		# Clone the SadTalker repository
		git clone https://github.com/engineervix/SadTalker.git
		cd SadTalker

		# Create a new conda environment and activate it
		source /opt/conda/etc/profile.d/conda.sh
		conda create -n sadtalker python=3.8 -y
		conda activate sadtalker

		# Upgrade pip and install required packages
		pip install --upgrade pip
		pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
		conda install ffmpeg -y
		pip install -r requirements.txt

		# Download models
		bash scripts/download_models.sh

		# do some monkeypatching
		# See https://github.com/OpenTalker/video-retalking/issues/224 for more details
		sed -i 's/from torchvision.transforms.functional_tensor import rgb_to_grayscale/from torchvision.transforms.functional import rgb_to_grayscale/' /opt/conda/envs/sadtalker/lib/python3.8/site-packages/basicsr/data/degradations.py

		# run SadTalker
		python inference.py --driven_audio ../audio.mp3 \
												--source_image ../image.png \
												--still \
												--preprocess full
												# Uncomment the following line if you want to use the enhancer (takes a while, but you get better results)
												# --enhancer gfpgan
EOF
} || handle_vastai_error

# now, back on the host machine ... let's get the generated file from the remote GPU instance
rsync -chavzP -e "ssh -o StrictHostKeyChecking=no -p $port -i $KEY_NAME" "$(basename "$ssh_url" | cut -d ':' -f 1)":~/SadTalker/results/*.mp4 sadtalker_output.mp4

# Destroy the GPU instance
vastai destroy instance "$instance_id"

# replace audio track with the "shiny" version
ffmpeg -i sadtalker_output.mp4 -i "$live_audio_file" -c:v copy -map 0:v:0 -map 1:a:0 -shortest video.mp4
# optimize the video
ffmpeg -i video.mp4 -vcodec libx264 -crf 28 "${live_audio_file%.*}.mp4"

# cleanup
rm -fv sadtalker_output.mp4 video.mp4 vast_* ssh_*.json

# post the video to social platform
cd "${HOME}/SITES/zed-news/" || { echo "Failed to change directory."; exit 1; }
invoke facebook-post

END_TIME=$(date +%s)
DURATION=$(( END_TIME - START_TIME ))
echo "Process completed in $DURATION seconds."
send_healthcheck_success
