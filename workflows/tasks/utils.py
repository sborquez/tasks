import os


def sanitize_string(path: str) -> str:
    """
    Sanitize a string to be used as a path or git branch name.

    Parameters
    ----------
    path : str
        The string to sanitize.

    Returns
    -------
    str
        The sanitized string.
    """
    for char in r'[]/ \?<>:|*@':
        path = path.replace(char, "_")
    return path.strip().encode("utf8", "ignore").decode("utf8", "ignore")

def is_running_in_docker() -> bool:
    """Check if the code is running inside a Docker container."""
    return os.path.exists("/.dockerenv")


def is_running_in_cloud_run_job() -> bool:
    """Check if the code is running inside a Google Cloud Run container."""
    """Check if the code is running inside a Google Cloud Run container."""
    return os.getenv("CLOUD_RUN_JOB") is not None
