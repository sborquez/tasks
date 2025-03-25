import os
import logging


def get_logger(module_name: str, func_name: str | None = None) -> logging.Logger:
    """
    Get a logger for the module with the given name. It use this format for the log messages:

    2021-08-25 15:00:00,000 | INFO | workflows.hello_world.workflow | Starting Hello World Workflow

    Parameters
    ----------
    module_name : str
        The name of the module for which the logger is required
    Returns
    -------
    logging.Logger
    """

    # Create a logger for the module
    if func_name:
        logger = logging.getLogger(f"{module_name}.{func_name}")
    else:
        logger = logging.getLogger(module_name)

    # Set the log level
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        log_level = 'INFO'
    logger.setLevel(getattr(logging, log_level))

    # Check if the logger has handlers already to prevent duplication
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


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


def normalize_string(string: str) -> str:
    """
    Normalize a string by removing leading and trailing whitespaces and converting it to lowercase.

    Parameters
    ----------
    string : str
        The string to normalize.

    Returns
    -------
    str
        The normalized string.
    """
    return sanitize_string(string).strip().lower()

def is_running_in_docker() -> bool:
    """Check if the code is running inside a Docker container."""
    return os.path.exists("/.dockerenv")


def is_running_in_cloud_run_job() -> bool:
    """Check if the code is running inside a Google Cloud Run container."""
    return os.getenv("CLOUD_RUN_JOB") is not None
