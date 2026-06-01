FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV CHROMIUM_PATH=/usr/bin/ungoogled-chromium

RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        chromium \
        chromium-driver \
        fonts-liberation \
        git \
        xvfb && \
    ln -sf /usr/bin/chromium /usr/bin/ungoogled-chromium && \
    ln -sf /usr/bin/chromium /usr/bin/chromium-browser && \
    chmod +x /usr/bin/chromium /usr/bin/chromedriver /usr/bin/ungoogled-chromium /usr/bin/chromium-browser || true && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /tmp/requirements.txt
