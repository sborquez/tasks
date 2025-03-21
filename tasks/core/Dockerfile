# Base stage - Install Python dependencies and build essentials
FROM python:3.12-slim AS base

# Install build essentials and git for repository handling
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container

COPY . ./core

RUN pip install --no-cache-dir ./core
