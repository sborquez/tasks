
# Base stage - Install Python dependencies and build essentials
ARG CORE_IMAGE=tasks-core:gpu-latest
ARG TASK_MODULE="speech_recognition"
FROM $CORE_IMAGE AS base

# Install gsutil
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
    > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && apt-get install -y google-cloud-sdk && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
ENV TASK_MODULE=$TASK_MODULE
COPY . ./task
RUN pip install --no-cache-dir ./task

# Set build-time argument for GCS model path
ARG SOURCE_MODEL_PATH=no_source_model_path
RUN mkdir -p /root/.cache

# Conditionally copy models based on SOURCE_MODEL_PATH scheme
RUN bash -c '\
  if [[ "$SOURCE_MODEL_PATH" == gs://* ]]; then \
    echo "Copying models from GCS: $SOURCE_MODEL_PATH"; \
    gsutil -m cp -r "$SOURCE_MODEL_PATH"/* "/root/.cache"; \
  else \
    echo "No models copied"; \
  fi'