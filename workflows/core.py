import logging
import time
import os

from typing import Any, Callable


__all__ = ['get_logger', 'task']


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


def task(func: Callable) -> Callable:
    """
    Decorator to log the start and end of a task.

    Parameters
    ----------
    func : Callable
        The function to decorate

    Returns
    -------
    Callable
    """

    def wrapper(*args: tuple, **kwargs: dict) -> Any:
        logger = get_logger(func.__module__)
        logger.info(f"Starting task: {func.__name__}")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"Task completed in {end_time - start_time:.2f} seconds")
        return result

    return wrapper
