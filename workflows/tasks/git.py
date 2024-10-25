import os

from prefect import task, get_run_logger
from git import Repo, GitCommandError


@task
def clone_repository(git_url: str, local_dir: str) -> str:
    """
    Clone a git repository to a local directory.

    Parameters
    ----------
    git_url : str
        The URL of the git repository to clone.
    local_dir : str
        The local directory path where the repository will be cloned.

    Returns
    -------
    str
        The path to the local directory where the repository was cloned.

    Notes
    -----
    If the local directory already exists, it will be cleaned up before cloning.
    """
    logger = get_run_logger()
    logger.debug(f"Cloning repository from {git_url} to {local_dir}")
    if os.path.exists(local_dir):
        logger.warning(f"Directory {local_dir} already exists. Cleaning up...")
        # Logic to clean up existing directory
        pass
    Repo.clone_from(git_url, local_dir)
    logger.debug(f"Repository cloned successfully to {local_dir}")
    return local_dir

@task
def create_branch(local_dir: str, branch_name: str) -> str:
    """
    Create a new branch in the local repository.

    Parameters
    ----------
    local_dir : str
        The path to the local repository.
    branch_name : str
        The name of the new branch to create.

    Returns
    -------
    str
        The name of the newly created branch.
    """
    logger = get_run_logger()
    logger.debug(f"Creating new branch '{branch_name}' in repository at {local_dir}")
    repo = Repo(local_dir)
    new_branch = repo.create_head(branch_name)
    new_branch.checkout()
    logger.debug(f"Branch '{branch_name}' created and checked out successfully")
    return branch_name

@task
def commit_changes(local_dir: str, commit_message: str) -> bool:
    """
    Commit changes in the local repository if changes are present.

    Parameters
    ----------
    local_dir : str
        The path to the local repository.
    commit_message : str
        The message to use for the commit.

    Returns
    -------
    bool
        True if a commit was made, False if no changes were found.

    Notes
    -----
    This function checks for both staged and untracked files before committing.
    If no changes are found, a warning message is printed.
    """
    logger = get_run_logger()
    logger.debug(f"Committing changes in repository at {local_dir}")
    repo = Repo(local_dir)
    if repo.is_dirty() or repo.untracked_files:
        repo.git.add(all=True)
        repo.index.commit(commit_message)
        logger.debug(f"Changes committed successfully with message: {commit_message}")
        return True
    else:
        logger.warning("No changes found in the repository. No commit was made.")
        return False

@task
def push_changes(local_dir: str, branch_name: str) -> bool:
    """
    Push changes from a local branch to the remote repository if there are unpushed commits.

    Parameters
    ----------
    local_dir : str
        The path to the local repository.
    branch_name : str
        The name of the branch to push.

    Returns
    -------
    bool
        True if changes were pushed, False if no unpushed commits were found.

    Notes
    -----
    This function checks for unpushed commits before pushing.
    If no unpushed commits are found, a warning message is printed.
    """
    logger = get_run_logger()
    logger.debug(f"Pushing changes from branch '{branch_name}' in repository at {local_dir}")
    repo = Repo(local_dir)
    origin = repo.remote(name="origin")
    origin.fetch()

    # Verify if the remote branch exists
    remote_branches = repo.git.branch('-r')
    if f'origin/{branch_name}' not in remote_branches:
        logger.debug(f"Branch 'origin/{branch_name}' does not exist. Pushing new branch.")
        try:
            origin.push(refspec=f"{branch_name}:{branch_name}")
            logger.debug(f"New branch '{branch_name}' pushed successfully")
            return True
        except GitCommandError as e:
            logger.error(f"Error pushing branch '{branch_name}': {e}")
            return False

    try:
        unpushed_commits = list(repo.iter_commits(f'origin/{branch_name}..{branch_name}'))

        if unpushed_commits:
            origin.push(refspec=f"{branch_name}:{branch_name}")
            logger.debug(f"Changes pushed successfully to branch '{branch_name}'")
            return True
        else:
            logger.warning(f"No unpushed commits found in branch '{branch_name}'. No push was made.")
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
#     logger = get_run_logger()
#     logger.debug(f"Pushing changes from branch '{branch_name}' in repository at {local_dir}")
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
#     logger = get_run_logger()
#     logger.debug(f"Pushing changes from branch '{branch_name}' in repository at {local_dir}")
#    pass