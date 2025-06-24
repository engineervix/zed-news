#!/usr/bin/env bash

# =================================================================================================
# description:  zed-news execution script, to be run by cron
# author:       Victor Miti <https://github.com/engineervix>
# url:          <https://github.com/engineervix/zed-news>
# version:      1.1.0
# license:      BSD-3-Clause
#
# Usage: ./cron.sh [digest|facebook-post|fx-update]
#
# Logical steps
# 1. cd to project directory
# 2. Activate virtual environment
# 3. Run specified task (digest in docker, facebook-post and fx-update natively)
# 4. commit changes (for digest and fx-update)
# 5. push changes to remote (for digest and fx-update)
# =================================================================================================

set -e  # Exit immediately if any command fails

# Check for required argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 [digest|facebook-post|fx-update]"
    echo "  digest        - Generate news digest using Docker"
    echo "  facebook-post - Post to Facebook (runs natively, no Docker)"
    echo "  fx-update     - Update foreign exchange rates (runs natively, no Docker)"
    exit 1
fi

TASK="$1"

# Validate task argument
if [[ "$TASK" != "digest" && "$TASK" != "facebook-post" && "$TASK" != "fx-update" ]]; then
    echo "Error: Invalid task '$TASK'. Must be 'digest', 'facebook-post', or 'fx-update'"
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
elif [[ "$TASK" == "fx-update" ]]; then
    PING_URL="${HEALTHCHECKS_FX_PING_URL}"
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
    inv facebook-post || {
        echo "Failed to run Facebook post task."
        send_healthcheck_failure
        exit 1
    }

    # Send success signal to healthchecks.io
    send_healthcheck_success

    echo "Facebook post task completed successfully."

elif [[ "$TASK" == "fx-update" ]]; then
    # Check if FX data is already up to date for today
    today_iso=$(date +"%Y-%m-%d")
    fx_current_file="app/web/_data/fx_current.json"

    if [[ -f "$fx_current_file" ]]; then
        # Extract the current_rates.date from the JSON file
        current_fx_date=$(jq -r '.current_rates.date' "$fx_current_file" 2>/dev/null || echo "")

        if [[ "$current_fx_date" == "$today_iso" ]]; then
            echo "FX rates are already up to date for today ($today_iso). Skipping update."
            send_healthcheck_success
            exit 0
        else
            echo "FX rates are from $current_fx_date, updating to $today_iso..."
        fi
    else
        echo "FX current file not found, proceeding with update..."
    fi

    echo "Running FX rates update task natively..."
    # Run FX update task natively (no Docker)
    inv fx-update || {
        echo "Failed to run FX update task."
        send_healthcheck_failure
        exit 1
    }

    # Commit FX data changes
    today=$(date  +"%Y-%m-%d %H:%M %Z")
    git add app/web/_data/fx_current.json app/web/_data/fx_data.json || { echo "Failed to stage FX data changes for commit."; send_healthcheck_failure; exit 1; }

    # Run pre-commit on the FX data files
    echo "Running pre-commit on FX data files..."
    if pre-commit run --files app/web/_data/fx_current.json app/web/_data/fx_data.json; then
        echo "Pre-commit passed - no issues found."
    else
        precommit_exit_code=$?
        if [[ $precommit_exit_code -eq 1 ]]; then
            echo "Pre-commit found and fixed issues. Re-staging files..."
        else
            echo "Pre-commit failed with exit code $precommit_exit_code"
            send_healthcheck_failure
            exit 1
        fi
    fi

    # Re-add files in case pre-commit made changes
    git add app/web/_data/fx_current.json app/web/_data/fx_data.json || { echo "Failed to re-stage FX data changes after pre-commit."; send_healthcheck_failure; exit 1; }

    git commit --no-verify -m "chore: 💱 fx rates update » ${today}" || { echo "Failed to commit FX data changes."; send_healthcheck_failure; exit 1; }

    # Push changes to remote
    git push origin main || { echo "Failed to push FX data changes to remote repository."; send_healthcheck_failure; exit 1; }

    # Send success signal to healthchecks.io
    send_healthcheck_success

    echo "FX rates update task completed successfully."
fi
