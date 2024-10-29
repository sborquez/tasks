from pydantic import BaseModel, Field
from workflows.tasks.git import clone_repository, create_branch, commit_changes, push_changes
from workflows.tasks.utility import create_temporary_dir, delete_temporary_dir
from workflows import get_logger, task
from random import randint


logger = get_logger(__name__)

class Parameters(BaseModel):
    git_url: str = Field(description="URL of the git repository to clone")
    git_user: str | None = Field(description="Git user name for configuration", default=None)
    git_email: str | None = Field(description="Git user email for configuration", default=None)


@task
def create_hello_world_file(local_dir: str) -> None:
    """
    Create a hello world file in the given directory.

    Parameters
    ----------
    local_dir : str
        The directory in which to create the file
    """
    logger.debug(f"Creating hello world file in directory: {local_dir}")
    with open(f"{local_dir}/hello_world.txt", "w") as f:
        f.write("Hello, World!")
    logger.debug("Hello world file created successfully")


def workflow(parameters: Parameters) -> None:
    logger.debug("Starting Hello World Workflow")
    git_url = parameters.git_url
    git_user = parameters.git_user
    git_email = parameters.git_email
    logger.debug(f"Git URL: {git_url}")
    if git_user and git_email:
        logger.debug(f"Git User: {git_user}")
        logger.debug(f"Git Email: {git_email}")
    else:
        logger.debug("Using system's Git configuration")

    logger.info("Starting Hello World Workflow")
    temp_dir = create_temporary_dir()
    repo_dir = clone_repository(git_url, temp_dir, git_user, git_email)
    branch = create_branch(repo_dir, f"hello-world-{randint(0, 1000):04}")
    create_hello_world_file(repo_dir)
    _ = commit_changes(repo_dir, "Add hello world file")
    pushed = push_changes(repo_dir, branch)
    if not pushed:
        logger.warning("Failed to push changes to remote repository")
        raise RuntimeError("Failed to push changes to remote repository")
    _ = delete_temporary_dir(temp_dir)
    logger.info("Hello World Workflow completed successfully")
