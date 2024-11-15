# Base stage - Install Python dependencies and build essentials
FROM python:3.12-slim AS base

# Install build essentials and git for repository handling
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container

COPY ./workflows ./workflows
COPY requirements.txt .

# Install the Python dependencies using local wheels and falling back to PyPI
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables with default values
ENV WORKFLOW_NAME="hello_world"

# COPY --from=registry.gitlab.com/codematos/pluscoder-repository:latest /bin/pluscoder /bin/pluscoder
COPY --from=gcr.io/pluscoder-workflows-441503/pluscoder:latest /bin/pluscoder /bin/pluscoder

# Set the entrypoint to run the workflows executable
ENTRYPOINT ["python", "-m", "workflows"]