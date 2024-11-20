# Base stage - Install Python dependencies and build essentials
FROM python:3.12-slim AS base

# Install build essentials and git for repository handling
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container

COPY ./workflows ./workflows
COPY requirements.txt .

# Install the Python dependencies using local wheels and falling back to PyPI
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables with default values
ENV WORKFLOW_NAME="hello_world"

ARG PLUSCODER_TOKEN
ARG PIP_TOKEN
ARG INSTALL_SCRIPT=https://gitlab.com/codematos/pluscoder-repository/-/raw/main/install.sh
RUN curl -sSL $INSTALL_SCRIPT -o install.sh
RUN bash install.sh -t $PLUSCODER_TOKEN -p $PIP_TOKEN -y -s

# Set the entrypoint to run the workflows executable
ENTRYPOINT ["python", "-m", "workflows"]
