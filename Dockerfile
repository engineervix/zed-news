FROM python:3.10-slim-bullseye

# Add user that will be used in the container
RUN groupadd zednews && \
    useradd --create-home --shell /bin/bash -g zednews zednews

RUN mkdir -p /home/zednews/app && chown zednews:zednews /home/zednews/app

# set work directory
WORKDIR /home/zednews/app

# set environment variables
# - Force Python stdout and stderr streams to be unbuffered.
ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/home/zednews/app

# Set timezone to Africa/Lusaka
RUN ln -fs /usr/share/zoneinfo/Africa/Lusaka /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata

# Install system dependencies required by the project
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    curl \
    git \
    ffmpeg \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Use user "zednews" to run the build commands below and the server itself.
USER zednews

# set up virtual environment & install python dependencies
ARG DEVELOPMENT
ENV VIRTUAL_ENV=/home/zednews/venv \
    DEVELOPMENT=${DEVELOPMENT}
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install pip-tools
COPY --chown=zednews ./requirements.txt .
COPY --chown=zednews ./requirements-dev.txt .
RUN python -m pip install -r requirements.txt ${DEVELOPMENT:+-r requirements-dev.txt}

# Copy the source code of the project into the container
COPY --chown=zednews:zednews . .

# Runtime command that executes when "docker run" is called
# basically, do nothing ... we'll run commands ourselves
CMD tail -f /dev/null
