from prefect import task, flow, get_run_logger
from pydantic import BaseModel, Field
from workflows.tasks.git import clone_repository, create_branch, commit_changes, push_changes
from workflows.tasks.utility import create_temporary_dir, delete_temporary_dir
from random import randint

class Parameters(BaseModel):
    git_url: str = Field(description="URL of the git repository to clone")
    git_user: str | None = Field(description="Git user name for configuration", default=None)
    git_email: str | None = Field(description="Git user email for configuration", default=None)


@task
def create_hello_world_file(local_dir: str) -> None:
    """
    Create a hello world file in the given directory.
    """
    logger = get_run_logger()
    logger.debug(f"Creating hello world file in directory: {local_dir}")
    with open(f"{local_dir}/hello_world.txt", "w") as f:
        f.write("Hello, World!")
    logger.debug("Hello world file created successfully")


@flow(name="Hello World Workflow")
def workflow(parameters: Parameters) -> None:
    logger = get_run_logger()
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
    temp_dir = create_temporary_dir()
    logger.debug(f"Temporary directory created: {temp_dir}")
    repo_dir = clone_repository(git_url, temp_dir, git_user, git_email)
    logger.debug(f"Repository cloned to: {repo_dir}")
    branch = create_branch(repo_dir, f"hello-world-{randint(0, 1000):04}")
    logger.debug(f"New branch created: {branch}")
    create_hello_world_file(repo_dir)
    logger.debug("Hello world file created")
    _ = commit_changes(repo_dir, "Add hello world file")
    logger.debug("Changes committed")
    _ = push_changes(repo_dir, branch)
    logger.debug(f"Changes pushed to branch: {branch}")
    _ = delete_temporary_dir(temp_dir)
    logger.debug(f"Temporary directory deleted: {temp_dir}")
    logger.debug("Hello World Workflow completed successfully")
