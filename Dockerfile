FROM ubuntu:24.04

# Remove shipped sudoer user (Required for Ubuntu 24.04 base)
# Create non-root user & required dirs
RUN touch /var/mail/ubuntu \
    && chown ubuntu /var/mail/ubuntu \
    && userdel -r ubuntu \
    && groupadd zednews \
    && useradd --create-home --shell /bin/bash -g zednews zednews \
    && mkdir -p /home/zednews/app \
    && chown zednews:zednews /home/zednews/app

# set work directory
WORKDIR /home/zednews/app

# set environment variables
# - Force Python stdout and stderr streams to be unbuffered.
ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/home/zednews/app

# Install system dependencies required by the project
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ Africa/Lusaka
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libssl-dev libffi-dev python3-dev python3-venv tzdata locales \
    curl \
    git \
    libpq-dev \
    postgresql-client \
    && apt-get autoremove \
    && apt-get clean

# Set timezone to Africa/Lusaka
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
    && dpkg-reconfigure tzdata

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Use user "zednews" to run the build commands below
USER zednews

# set up virtual environment & install python dependencies
ARG POETRY_VERSION=2.1.3
ARG DEVELOPMENT
ENV VIRTUAL_ENV=/home/zednews/venv \
    DEVELOPMENT=${DEVELOPMENT}
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip setuptools
RUN python -m pip install poetry==$POETRY_VERSION
COPY --chown=zednews ./pyproject.toml .
COPY --chown=zednews ./poetry.lock .
RUN poetry install ${DEVELOPMENT:+--with dev} --no-root

# Copy the source code of the project into the container
COPY --chown=zednews:zednews . .
RUN poetry install --only-root

# Runtime command that executes when "docker run" is called
# basically, do nothing ... we'll run commands ourselves
CMD tail -f /dev/null
