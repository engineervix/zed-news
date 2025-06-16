#!/usr/bin/env bash

# =================================================================================================
# description:  zed-news execution script, to be run by cron
# author:       Victor Miti <https://github.com/engineervix>
# url:          <https://github.com/engineervix/zed-news>
# version:      1.0.0
# license:      BSD-3-Clause
#
# Usage: ./cron.sh [digest|facebook-post]
#
# Logical steps
# 1. cd to project directory
# 2. Activate virtual environment
# 3. Run specified task (digest in docker or facebook-post natively)
# 4. commit changes (only for digest)
# 5. push changes to remote (only for digest)
# =================================================================================================

set -e  # Exit immediately if any command fails

# Check for required argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 [digest|facebook-post]"
    echo "  digest        - Generate news digest using Docker"
    echo "  facebook-post - Post to Facebook (runs natively, no Docker)"
    exit 1
fi

TASK="$1"

# Validate task argument
if [[ "$TASK" != "digest" && "$TASK" != "facebook-post" ]]; then
    echo "Error: Invalid task '$TASK'. Must be 'digest' or 'facebook-post'"
    exit 1
fi

# 1. cd to project directory
cd "${HOME}/SITES/tools/zed-news" || { echo "Failed to change directory."; exit 1; }

# Source the .env file so we can retrieve healthchecks.io ping URL
# shellcheck source=/dev/null
source .env

# Set healthchecks URL based on task
if [[ "$TASK" == "digest" ]]; then
    PING_URL="${HEALTHCHECKS_PING_URL}"
elif [[ "$TASK" == "facebook-post" ]]; then
    PING_URL="${HEALTHCHECKS_FACEBOOK_PING_URL}"
fi

# Function to send success signal to healthchecks.io
function send_healthcheck_success() {
  curl -fsS --retry 3 "${PING_URL}" > /dev/null
}

# Function to send failure signal to healthchecks.io
function send_healthcheck_failure() {
  curl -fsS --retry 3 "${PING_URL}/fail" > /dev/null
}

# 2. Activate virtual environment
# shellcheck source=/dev/null
source "${HOME}/Env/zed-news/bin/activate" || { echo "Failed to activate virtual environment."; send_healthcheck_failure; exit 1; }

# 3. Run specified task
if [[ "$TASK" == "digest" ]]; then
    git pull || { echo "Failed to pull changes from Git."; send_healthcheck_failure; exit 1; }
    echo "Running digest task in Docker..."
    # Build and run digest in docker container
    inv up --build || { echo "Failed to build Docker container."; send_healthcheck_failure; exit 1; }
    docker compose run --rm app invoke digest || {
        echo "Failed to run digest script inside Docker container."
        send_healthcheck_failure
        exit 1
    }
    inv down || { echo "Failed to stop Docker container."; send_healthcheck_failure; exit 1; }

    # 5. commit changes (only for digest)
    today_iso=$(date --iso)
    git add app/web/_pages/news || { echo "Failed to stage changes for commit."; send_healthcheck_failure; exit 1; }
    git commit --no-verify -m "chore: 📰 news digest » ${today_iso}" || { echo "Failed to commit changes."; send_healthcheck_failure; exit 1; }

    # 6. push changes to remote (only for digest)
    git push origin main || { echo "Failed to push changes to remote repository."; send_healthcheck_failure; exit 1; }

    # Send success signal to healthchecks.io
    send_healthcheck_success

    # Pause for 5 minutes
    sleep 300

    # Notify Admin via Apprise + ntfy.sh
    today_human_readable=$(date +"%a %d %b %Y")
    apprise -vv -t "📰 News Digest » ${today_human_readable}" \
      -b "📖 Read today's news at ${BASE_URL}/news/${today_iso}/" \
      "${APPRISE_NTFY_URL}"

elif [[ "$TASK" == "facebook-post" ]]; then
    echo "Running Facebook post task natively..."
    # Run facebook post task natively (no Docker)
    inv facebook_post || {
        echo "Failed to run Facebook post task."
        send_healthcheck_failure
        exit 1
    }

    # Send success signal to healthchecks.io
    send_healthcheck_success

    echo "Facebook post task completed successfully."
fi
