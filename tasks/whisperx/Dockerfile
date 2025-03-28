
# Base stage - Install Python dependencies and build essentials
ARG CORE_IMAGE=tasks-core:gpu-latest
ARG TASK_MODULE="whisperx"
FROM $CORE_IMAGE AS base

# Install build essentials and git for repository handling
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Download models
ENV MODEL_DIR=/models



# Set the working directory in the container
ENV TASK_MODULE=${TASK_MODULE}
COPY . ./task
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cu126 ./task
