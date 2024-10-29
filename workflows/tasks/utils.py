import os


def is_running_in_docker() -> bool:
    """Check if the code is running inside a Docker container."""
    return os.path.exists('/.dockerenv')


def is_running_in_cloud_run_job() -> bool:
    """Check if the code is running inside a Google Cloud Run container."""
    """Check if the code is running inside a Google Cloud Run container."""
    return os.getenv("CLOUD_RUN_JOB") is not None
