import shutil
import os
from importlib import util
from typing import Callable

from workflows import get_logger, task

logger = get_logger(__name__)


def _get_pluscoder() -> Callable:
    # Check if PlusCoder is importable
    if util.find_spec("pluscoder"):
        logger.debug("PlusCoder found as a module")
        _pluscoder = ["python", "-m", "pluscoder"]
    # Find PlusCoder Binary
    elif shutil.which("pluscoder"):
        logger.debug("PlusCoder found as a binary")
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
    prompt = f"I received the following feature request: <feature_request>{prompt}</feature_request>. Implement the feature delegating the work if necessary."
    output = pluscoder([
        "--dev",
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
