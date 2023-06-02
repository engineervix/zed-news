#!/usr/bin/env bash

# =================================================================================================
# description:  zed-news execution script, to be run by cron
# author:       Victor Miti <https://github.com/engineervix>
# url:          <https://github.com/engineervix/zed-news>
# version:      0.1.0
# license:      BSD-3-Clause
#
# Logical steps
# 1. cd to project directory
# 2. Activate virtual environment
# 3. git pull
# 4. Run script inside docker container
# 5. commit changes
# 6. push changes to remote
# 7. deactivate virtual environment
# 8. stop docker container
# =================================================================================================

set -e  # Exit immediately if any command fails

# 1. cd to project directory
cd "${HOME}/SITES/zed-news" || { echo "Failed to change directory."; exit 1; }

# 2. Activate virtual environment
# shellcheck source=/dev/null
source "${HOME}/Env/zed-news/bin/activate" || { echo "Failed to activate virtual environment."; exit 1; }

# 3. git pull
git pull || { echo "Failed to pull changes from Git."; exit 1; }

# 4. Run script inside docker container
docker-compose run --rm app invoke toolchain || { echo "Failed to run script inside Docker container."; exit 1; }

# 5. commit changes
today_iso=$(date --iso)
git add . || { echo "Failed to stage changes for commit."; exit 1; }
git commit --no-verify -m "chore: ✨ new episode 🎙️ - ${today_iso}" || { echo "Failed to commit changes."; exit 1; }

# 6. push changes to remote
git push origin main || { echo "Failed to push changes to remote repository."; exit 1; }
