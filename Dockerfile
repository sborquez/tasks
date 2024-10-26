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
ENV WORKFLOW_NAME="hello_world" \
    PREFECT_LOGGING_LEVEL="INFO"

# Copy an executable from the pluscode:latest image
# COPY --from=pluscode:latest /bin/pluscode /bin/pluscode

# Set the entrypoint to run the workflows executable
ENTRYPOINT ["python", "-m", "workflows"]