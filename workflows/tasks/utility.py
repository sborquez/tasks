from prefect import task, get_run_logger
import tempfile
import shutil
import os

@task
def create_temporary_dir() -> str:
    """
    Create a temporary directory.

    Returns:
    --------
    str
        The path to the created temporary directory.
    """
    logger = get_run_logger()
    temp_dir = tempfile.mkdtemp()
    logger.debug(f"Created temporary directory: {temp_dir}")
    return temp_dir

@task
def delete_temporary_dir(temp_dir: str) -> None:
    """
    Delete a temporary directory and its contents.

    Parameters:
    -----------
    temp_dir : str
        The path to the temporary directory to be deleted.
    """
    logger = get_run_logger()
    if os.path.exists(temp_dir):
        logger.debug(f"Deleting temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)
        logger.debug(f"Temporary directory deleted: {temp_dir}")
    else:
        logger.warning(f"Temporary directory not found: {temp_dir}")