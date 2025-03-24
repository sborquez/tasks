# Base stage - Install Python dependencies and build essentials
FROM python:3.12-slim AS base

# Install build essentials and git for repository handling
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*
COPY . ./core
RUN pip install --no-cache-dir ./core

# Set needed environment variables
ENV FIRESTORE_PROJECT_ID=
ENV FIRESTORE_DATABASE=
ENV FIRESTORE_EMULATOR_HOST=

# Run the tasks
ENV TASK_COMMAND=tasks-run
ENTRYPOINT ["./core/entrypoint.sh"]