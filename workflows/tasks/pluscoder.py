import shutil
import os
from importlib import util
from typing import Callable
import json

from workflows import get_logger, task

logger = get_logger(__name__)


def _get_pluscoder() -> Callable:
    # Check if PlusCoder is importable
    if util.find_spec("pluscoder"):
        logger.debug("PlusCoder found as a module")
        _pluscoder = ["python", "-m", "pluscoder"]
    # Find PlusCoder Binary
    elif shutil.which("pluscoder"):
        logger.debug("PlusCoder found")
        _pluscoder = ["pluscoder"]
    # Find PlusCoder UV
    elif os.path.exists(os.path.join(os.path.expanduser("~"), ".local/bin/pluscoder")):
        logger.debug("PlusCoder found as a UV tool")
        _pluscoder = [os.path.join(os.path.expanduser("~"), ".local/bin/pluscoder")]
    else:
        raise ImportError("PlusCoder not found")

    def _run_pluscoder(args: list) -> str:
        import subprocess
        output = subprocess.run(_pluscoder + args, check=True, capture_output=True)
        return output.stdout.decode("utf-8")
    return _run_pluscoder

@task
def add_pluscoder_gitignore(working_dir: str) -> bool:
    """
    Add the PlusCoder gitignore file to the working directory

    Parameters:
    -----------
    working_dir : str
        The directory to add the gitignore file to

    Returns:
    --------
    bool
        The result of the operation
    """
    cwd = os.getcwd()
    os.chdir(working_dir)
    added = False
    if not os.path.exists(".gitignore"):
        with open(".gitignore", "w") as f:
            f.write(".pluscoder/")
        added = True
    else:
        # Check if .pluscoder is already in the gitignore
        import re
        with open(".gitignore", "r") as f:
            gitignore = f.read()
        if not re.search(r"\.pluscoder/", gitignore):
            with open(".gitignore", "a") as f:
                f.write("\n.pluscoder/")
            added = True
    os.chdir(cwd)
    return added


@task
def run_single_prompt(working_dir: str, prompt: str, provider: str, model: str, agent: str, **extra_flags: dict) -> str:
    """
    Run a single prompt through PlusCoder

    Parameters:
    -----------
    prompt : str
        The prompt to be run through the API.
    provider : str
        The provider to be used for the API.
    model : str
        The model to be used
    agent : str
        The agent to be used for the API.
    extra_flags : dict
        The configuration to be used for the API
    Returns:
    --------
    bool
        The result of the API call.
    """
    pluscoder = _get_pluscoder()
    cwd = os.getcwd()
    os.chdir(working_dir)
    prompt = f"I received the following feature request: <feature_request>{prompt}</feature_request>. Generate a task list and delegate it immediately."
    output = pluscoder([
        "--dev",
        "--debug",
        "--no-init",
        "--user_input", prompt,
        "--provider", provider,
        "--model", model,
        "--default_agent", agent,
        "--auto_confirm", "true",
        "--auto_commits", "false",
    ])
    os.chdir(cwd)
    return output


@task
def run_task_list_prompt(working_dir: str, task_list_encoded: str | dict, provider: str, model: str, agent: str, **extra_flags: dict) -> str:
    """
    Run a single prompt through PlusCoder

    Parameters:
    -----------
    tasks_list_encoded : str | dict
        The JSON encoded task list to be run through the API.
    provider : str
        The provider to be used for the API.
    model : str
        The model to be used
    agent : str
        The agent to be used for the API.
    extra_flags : dict
        The configuration to be used for the API
    Returns:
    --------
    bool
        The result of the API call.
    """
    pluscoder = _get_pluscoder()
    cwd = os.getcwd()
    os.chdir(working_dir)
    if isinstance(task_list_encoded, str):
        task_list_encoded = json.loads(task_list_encoded)

    with open("./task_list.json", "w") as f:
        json.dump(task_list_encoded, f)

    # Log pluscoder version
    pluscoder_version = str(pluscoder(["--version"]))
    logger.debug("Running PlusCoder Version: " + pluscoder_version)

    logger.info("Running PlusCoder with task list...")
    output = pluscoder([
        "--dev",
        "--debug",
        "--no-init",
        "--task_list", "./task_list.json",
        "--provider", provider,
        "--model", model,
        "--default_agent", agent,
        "--auto_confirm", "true",
        "--auto_commits", "false",
    ])

    # Delete task json file
    os.remove("./task_list.json")
    os.chdir(cwd)
    return output
