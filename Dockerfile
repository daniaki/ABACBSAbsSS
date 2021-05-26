FROM python:3.6 AS base

###############################################################################
# Base configuration stage
###############################################################################
FROM base as builder

ENV APP_USER=abacbs

# Update the default application repository sources list and install
# required dependencies
RUN useradd -m ${APP_USER}
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y build-essential cron

RUN mkdir -p /srv/app
RUN mkdir -p /srv/app/logs
RUN mkdir -p /srv/app/static
RUN mkdir -p /srv/app/media

WORKDIR /srv/app

COPY requirements/base.txt .
COPY requirements/production.txt .
RUN pip3 install --no-cache-dir -r base.txt
RUN pip3 install --no-cache-dir -r production.txt

###############################################################################
# App configuration stage
###############################################################################
FROM builder as app

WORKDIR /srv/app

COPY . .

RUN chown -R ${APP_USER}:${APP_USER} /srv/app

# Copy entrypoint script into the image
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Port to expose for external comms
EXPOSE 8000

# Run entrypoint script in maveric source root
USER ${APP_USER}
WORKDIR /srv/app

ENTRYPOINT ["docker-entrypoint.sh"]
