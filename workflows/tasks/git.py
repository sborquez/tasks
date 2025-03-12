import os

from git import Repo, GitCommandError

from workflows import get_logger, task
from workflows.tasks.utils import is_running_in_docker, is_running_in_cloud_run_job


logger = get_logger(__name__)

def add_token_to_git_http_url(git_url, token):
    """
    Add a token to a git URL for authentication.

    Parameters
    ----------
    git_url : str
        The URL of the git repository.
    token : str
        The token to add to the URL.

    Returns
    -------
    str
        The git URL with the token added.
    """
    # Check if is gitlab
    if "gitlab" in git_url:
        return git_url.replace("https://", f"https://__token__:{token}@")
    else:
        return git_url.replace("https://", f"https://{token}@")

@task
def clone_repository(
    git_url: str, working_dir: str, git_user: str | None = None, git_email: str | None = None
) -> str:
    """
    Clone a git repository to a directory and configure git user and email.

    Parameters
    ----------
    git_url : str
        The URL of the git repository to clone.
    working_dir : str
        The directory path where the repository will be cloned.
    git_user : str, optional
        The Git user name to configure. If None, uses the system's Git configuration.
    git_email : str, optional
        The Git user email to configure. If None, uses the system's Git configuration.

    Returns
    -------
    str
        The path to the directory where the repository was cloned.

    Notes
    -----
    If the directory already exists, it will be cleaned up before cloning.
    Git user and email will be configured for the cloned repository if provided.
    """
    logger.debug(f"Cloning repository from {git_url} to {working_dir}")

    #if is_running_in_docker() or is_running_in_cloud_run_job():
    if True:
        logger.debug("Running in Docker environment")
        # Docker environment: Use token-based authentication
        if git_url.startswith("https://"):
            # TODO: differentiate between GitHub and GitLab URLs
            if "GIT_TOKEN" not in os.environ:
                raise ValueError("GIT_TOKEN environment variable is not set.")
            git_token = os.getenv("GIT_TOKEN")
            git_url = add_token_to_git_http_url(git_url, git_token)
        elif git_url.startswith("git@"):
            raise ValueError("SSH URLs are not supported in Docker. Please use HTTPS URLs.")
        else:
            raise ValueError("Unsupported git URL format.")
    else:
        # User environment: Use system's Git configuration
        logger.debug("Using system's Git configuration for authentication")

    repo = Repo.clone_from(git_url, working_dir)
    logger.debug(f"Repository cloned successfully to {working_dir}")

    # Configure Git user and email if provided
    if git_user and git_email:
        logger.debug(f"Configuring Git user: {git_user} and email: {git_email}")
        repo.git.config("user.name", git_user)
        repo.git.config("user.email", git_email)
        logger.debug("Git user and email configured successfully")
    else:
        logger.debug("Using system's Git user and email configuration")

    return working_dir


@task
def change_branch(working_dir: str, branch_name: str) -> tuple[str, bool]:
    """
    Change the current branch in the local repository.

    Parameters
    ----------
    working_dir : str
        The path to the local repository.
    branch_name : str
        The name of the branch to switch to.

    Returns
    -------
    str
        The name of the branch that was switched to.
    bool
        True if the branch was switched successfully, False if the branch does not exist.
    """
    logger.debug(f"Switching to branch '{branch_name}' in repository at {working_dir}")
    repo = Repo(working_dir)
    # Check if branch is different from the current branch
    if branch_name == str(repo.active_branch):
        logger.debug(f"Branch '{branch_name}' is already the current branch")
        return branch_name, True

    # Check if the branch exists in remote
    elif branch_name in list(map(lambda s: str(s).replace("origin/", ""), repo.remotes.origin.refs)):
        # Check if the branch exists in local
        repo.git.checkout(branch_name)
        logger.debug(f"Branch switched to '{branch_name}' successfully")
        repo.git.pull()
        return branch_name, True

    # Branch does not exist
    else:
        logger.warning(f"Branch '{branch_name}' does not exist in the repository.")
        current_branch = str(repo.active_branch)
        return current_branch, False


@task
def create_branch(working_dir: str, branch_name: str) -> str:
    """
    Create a new branch in the local repository.

    Parameters
    ----------
    working_dir : str
        The path to the local repository.
    branch_name : str
        The name of the new branch to create.

    Returns
    -------
    str
        The name of the newly created branch.
    """
    logger.debug(f"Creating new branch '{branch_name}' in repository at {working_dir}")
    repo = Repo(working_dir)
    new_branch = repo.create_head(branch_name)
    new_branch.checkout()
    logger.debug(f"Branch '{branch_name}' created and checked out successfully")
    return branch_name


@task
def commit_changes(working_dir: str, commit_message: str | None = None, just_add: bool = False) -> bool:
    """
    Commit changes in the local repository if changes are present.

    Parameters
    ----------
    working_dir : str
        The path to the local repository.
    commit_message : str | None, optional
        The message to use for the commit. If None, uses a default message generated by Git.
    just_add : bool, optional
        If True, only add files to the staging area without committing.
    Returns
    -------
    bool
        True if a commit was made, False if no changes were found.

    Notes
    -----
    This function checks for both staged and untracked files before committing.
    If no changes are found, a warning message is printed.
    """
    logger.debug(f"Committing changes in repository at {working_dir}")
    repo = Repo(working_dir)
    if repo.is_dirty() or repo.untracked_files:
        repo.git.add(all=True)
        if just_add:
            logger.debug("Changes added to staging area. No commit was made.")
            return False
        if commit_message is None or commit_message == "":
            changed_files = [item.a_path for item in repo.index.diff("HEAD")]
            commit_message = "Updated files: " + ", ".join(changed_files)
        repo.index.commit(commit_message)
        logger.debug(f"Changes committed successfully with message: {commit_message}")
        return True
    else:
        logger.warning("No changes found in the repository. No commit was made.")
        return False


@task
def push_changes(working_dir: str, branch_name: str) -> bool:
    """
    Push changes from a local branch to the remote repository if there are non-pushed commits.

    Parameters
    ----------
    working_dir : str
        The path to the local repository.
    branch_name : str
        The name of the branch to push.

    Returns
    -------
    bool
        True if changes were pushed, False if no non-pushed commits were found.

    Notes
    -----
    This function checks for non-pushed commits before pushing.
    If no non-pushed commits are found, a warning message is printed.
    """
    logger.debug(f"Pushing changes from branch '{branch_name}' in repository at {working_dir}")
    repo = Repo(working_dir)
    origin = repo.remote(name="origin")
    origin.fetch()

    # Verify if the remote branch exists
    remote_branches = repo.git.branch("-r")
    if f"origin/{branch_name}" not in map(str.strip, remote_branches.split("\n")):
        logger.debug(f"Branch 'origin/{branch_name}' does not exist. Pushing new branch.")
        try:
            origin.push(refspec=f"{branch_name}:{branch_name}")
            logger.debug(f"New branch '{branch_name}' pushed successfully")
            return True
        except GitCommandError as e:
            logger.error(f"Error pushing branch '{branch_name}': {e}")
            return False

    try:
        non_pushed_commits = list(repo.iter_commits(f"origin/{branch_name}..{branch_name}"))

        if non_pushed_commits:
            origin.push(refspec=f"{branch_name}:{branch_name}")
            logger.debug(f"Changes pushed successfully to branch '{branch_name}'")
            return True
        else:
            logger.warning(
                f"No unpushed commits found in branch '{branch_name}'. No push was made."
            )
            return False
    except GitCommandError as e:
        logger.error(f"Error checking commits for branch '{branch_name}': {e}")
        return False


# @task
# def create_pull_request_github(repo_name: str, branch_name: str, base_branch: str) -> None:
#     """
#     Create a pull request on GitHub.
#
#     Parameters
#     ----------
#     repo_name : str
#         The name of the repository on GitHub.
#     branch_name : str
#         The name of the branch to create the pull request from.
#     base_branch : str
#         The name of the branch to merge into.
#
#     Returns
#     -------
#     None
#
#     Notes
#     -----
#     This function requires a GitHub token to be set in the environment variables.
#     """
#     from github import Github
#     logger.debug(f"Pushing changes from branch '{branch_name}' in repository at {working_dir}")
#     git_token = os.getenv('GITHUB_TOKEN')
#     g = Github(git_token)
#     user = g.get_user()
#     repo = user.get_repo(repo_name)
#     pr = repo.create_pull(
#         title=f'Automated PR for {branch_name}',
#         body='This PR was created automatically.',
#         head=branch_name,
#         base=base_branch
#     )
#     print(f"Pull Request created: {pr.html_url}")

# @task
# def create_pull_request_gitlab(repo_name: str, branch_name: str, base_branch: str) -> None:
#    """
#    Create a pull request on GitLab.
#
#    Parameters
#    ----------
#    repo_name : str
#        The name of the repository on GitLab.
#    branch_name : str
#        The name of the branch to create the pull request from.
#    base_branch : str
#        The name of the branch to merge into.
#
#    Returns
#    -------
#    None
#
#    Notes
#    -----
#    This function is a placeholder for GitLab pull request creation logic.
#    """
#     logger.debug(f"Pushing changes from branch '{branch_name}' in repository at {working_dir}")
#    pass
