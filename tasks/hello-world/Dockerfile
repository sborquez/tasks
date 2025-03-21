
# Base stage - Install Python dependencies and build essentials
ARG CORE_IMAGE=tasks-core:latest
FROM $CORE_IMAGE AS base

# Set the working directory in the container
ENV TASK_MODULE="hello_world"
COPY . ./task
RUN pip install --no-cache-dir ./task

# COPY --from=registry.gitlab.com/codematos/pluscoder-repository:latest /bin/pluscoder /bin/pluscoder
# COPY --from=gcr.io/pluscoder-workflows-441503/pluscoder:latest /bin/pluscoder /bin/pluscoder