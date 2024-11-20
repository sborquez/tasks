from pydantic import BaseModel, Field
from workflows.tasks.git import (
    clone_repository,
    create_branch,
    push_changes,
    change_branch,
    commit_changes,
)
from workflows.tasks.utility import create_temporary_dir, delete_temporary_dir
from workflows.tasks.pluscoder import run_single_prompt
from workflows.tasks.utils import sanitize_string
from workflows import get_logger
from random import randint

MAX_RETRIES = 3
DEFAULT_AGENT = "orchestrator"
# DEFAULT_MODEL = "claude-3-5-sonnet-latest"
# DEFAULT_PROVIDER = "anthropic"
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt4o"

PROTECTED_BRANCH_NAMES = ("main", "master", "develop")

logger = get_logger(__name__)


class Parameters(BaseModel):
    git_url: str = Field(description="URL of the git repository to clone")
    source_branch: str | None = Field(
        description="Source branch to create the feature branch from", default=None
    )
    feature_branch: str | None = Field(
        description="Name of the feature branch to create. If None, a branch will be created automatically",  # noqa
        default=None,
    )
    author: str | None = Field(description="Author name for configuration", default=None)
    git_user: str | None = Field(description="Git user name for configuration", default=None)
    git_email: str | None = Field(description="Git user email for configuration", default=None)
    feature_request: str = Field(description="Feature request to be implemented")
    agent: str | None = Field(
        description="Name of the agent to use for PlusCoder", default=DEFAULT_AGENT
    )
    model: str | None = Field(
        description="Name of the model to use for PlusCoder", default=DEFAULT_MODEL
    )
    provider: str | None = Field(
        description="Name of the provider to use for PlusCoder", default=DEFAULT_PROVIDER
    )
    extra_flags: dict | None = Field(
        description="Extra flags to be passed to the PlusCoder API", default=None
    )


def workflow(parameters: Parameters) -> None:
    logger.debug("Start PlusCoder Workflow")
    git_url = parameters.git_url
    source_branch = parameters.source_branch
    feature_branch = parameters.feature_branch
    author = parameters.author
    git_user = parameters.git_user
    git_email = parameters.git_email
    feature_request = parameters.feature_request
    agent = parameters.agent
    model = parameters.model
    provider = parameters.provider
    extra_flags = parameters.extra_flags or dict()
    logger.debug(f"Git URL: {git_url}")
    if git_user and git_email:
        logger.debug(f"Git User: {git_user}")
        logger.debug(f"Git Email: {git_email}")
    else:
        logger.debug("Using system's Git configuration")

    if source_branch:
        logger.debug(f"Source Branch: {source_branch}")
    if author:
        logger.debug(f"Author: {author}")

    logger.debug(f"Feature Request: {feature_request}")
    logger.debug(f"Model: {model}")
    logger.debug(f"Provider: {provider}")
    logger.debug(f"Extra Flags: {extra_flags}")

    logger.info("Starting PlusCoder Workflow")
    temp_dir = create_temporary_dir()
    repo_dir = clone_repository(git_url, temp_dir, git_user, git_email)
    if source_branch:
        logger.debug(f"Changing branch to {source_branch}")
        _ = change_branch(repo_dir, source_branch)
    if feature_branch and feature_branch not in PROTECTED_BRANCH_NAMES and feature_branch != source_branch:
        feature_branch = sanitize_string(feature_branch)
    elif author:
        # Create a branch compatible author name
        sanitized_author = sanitize_string(author)
        feature_branch = f"feature/{sanitized_author}-{randint(0, 1000):04}"
    else:
        feature_branch = f"feature/pluscoder-{randint(0, 1000):04}"
    logger.info(f"Working in new branch: {feature_branch}")
    branch = create_branch(repo_dir, feature_branch)
    retries = MAX_RETRIES
    logger.info(f"Running PlusCoder with {retries} retries")
    while retries > 0:
        result = run_single_prompt(
            repo_dir,
            feature_request,
            provider,
            model,
            agent,
        )
        logger.debug(f"PlusCoder result: {result}")
        # TODO: This actually doesn't check if the code was generated successfully, just that the process ran.
        if result:
            break
        retries -= 1
        logger.debug(f"Failed to run PlusCoder, retrying. Retries left: {retries}")
    logger.debug("PlusCoder completed successfully")
    logger.debug("Committing changes to repository")
    _ = commit_changes(repo_dir)
    logger.debug("Pushing changes to repository")
    pushed = push_changes(repo_dir, branch)
    if not pushed:
        logger.warning("Failed to push changes to remote repository")
        raise RuntimeError("Failed to push changes to remote repository")
    _ = delete_temporary_dir(temp_dir)
    logger.info("Push Feature Workflow completed successfully")
