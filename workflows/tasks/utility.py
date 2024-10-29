import tempfile
import shutil
import os

from workflows import get_logger, task

logger = get_logger(__name__)


@task
def create_temporary_dir() -> str:
    """
    Create a temporary directory.

    Returns:
    --------
    str
        The path to the created temporary directory.
    """
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
    if os.path.exists(temp_dir):
        logger.debug(f"Deleting temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)
        logger.debug(f"Temporary directory deleted: {temp_dir}")
    else:
        logger.warning(f"Temporary directory not found: {temp_dir}")