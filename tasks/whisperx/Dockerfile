
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

# Install gsutil
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-sdk

# Download models
RUN mkdir -p /models
ENV MODEL_DIR=/models

# Set the working directory in the container
ENV TASK_MODULE=${TASK_MODULE}
COPY . ./task
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cu126 ./task

# Set build-time argument for GCS model path
ARG SOURCE_MODEL_PATH=no_source_model_path

# Conditionally copy models based on SOURCE_MODEL_PATH scheme
RUN bash -c '\
  if [[ "$SOURCE_MODEL_PATH" == gs://* ]]; then \
    echo "Copying models from GCS: $SOURCE_MODEL_PATH"; \
    gsutil -m cp -r "$SOURCE_MODEL_PATH"/* "$MODEL_DIR"; \
  else \
    echo "No models copied"; \
  fi'