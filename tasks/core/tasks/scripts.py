import argparse
import importlib
import os
import json

from tasks.types import TaskWithJobIdType, JobIDType, BaseParameters, BaseResult
from tasks.db import create_task, get_firestore_client
from tasks.utils import get_logger, normalize_string


logger = get_logger(__name__)


def import_task(task_module: str) -> tuple[TaskWithJobIdType, type[BaseParameters], type[BaseResult]]:
    """
    Import a task module and return the task function, parameters model, and results model.
    """
    try:
        module = importlib.import_module(task_module)
    except ModuleNotFoundError as e:
        logger.error(f"Task {task_module} not found")
        raise ValueError(f"Task {task_module} not found") from e
    try:
        task = getattr(module, "task")
    except AttributeError as e:
        logger.error("Task \"task\" function not found")
        raise ValueError("Task \"task\" function not found") from e
    try:
        Parameters = getattr(module, "Parameters")
    except AttributeError as e:
        logger.error(f"Parameters not found for task {task_module}")
        raise ValueError(f"Parameters not found for task {task_module}") from e
    try:
        Results = getattr(module, "Results")
    except AttributeError as e:
        logger.error(f"Results not found for task {task_module}")
        raise ValueError(f"Results not found for task {task_module}") from e
    return task, Parameters, Results


def parse_register_parameters(task_name: str) -> str:
    """
    Parse and validate input parameters for a task.

    Parameters:
    -----------
    task_name: str
        Name of the task.

    Returns:
    --------
    str
        Identifier to the task location. e.g. the Cloud Run job name with the format 'projects/{project_id}/locations/{location}/jobs/{job_id}'

    Raises:
        ValueError: If required parameters are missing or invalid.
    """
    parser = argparse.ArgumentParser(
        description=f"Register {task_name.replace('_', ' ').title()} workflow",
    )
    # Add job_id argument
    parser.add_argument(
        '--task_uri',
        required=True,
        help="Identifier to the task location. e.g. the Cloud Run job name with the format 'projects/{project_id}/locations/{location}/jobs/{job_id}'",
    )
    args = parser.parse_args()
    return args.task_uri


def register_task(task_pipeline: TaskWithJobIdType, parameters_model: type[BaseParameters], results_model: type[BaseResult]) -> None:
    """
    Register a task pipeline with input parameters and results models, and store it in Firestore.

    Parameters
    ----------
    task_pipeline : TaskWithJobIdType
        Task pipeline function.
    parameters_model : type[BaseParameters]
        Parameters model for the task.
    results_model : type[BaseResult]
        Results model for the task.

    Returns
    -------
    None
    """
    # Register task in Firestore
    logger.info(f"Registering task {task_pipeline.__name__}")
    task_name = task_pipeline.task_name if hasattr(task_pipeline, "task_name") else task_pipeline.__name__
    task_id = task_pipeline.task_id if hasattr(task_pipeline, "task_id") else normalize_string(task_name)
    task_uri = parse_register_parameters(task_name)
    task_description = task_pipeline.task_description if hasattr(task_pipeline, "task_description") else task_pipeline.__doc__ or ""
    parameters_json_schema = json.dumps(parameters_model.model_json_schema())
    results_json_schema = json.dumps(results_model.model_json_schema())
    db = get_firestore_client()
    create_task(db, task_id, task_name, task_description, parameters_json_schema, results_json_schema, task_uri)


def parse_run_parameters(task_name: str, parameters_model: type[BaseParameters]) -> tuple[JobIDType, BaseParameters]:
    """
    Parse and validate input parameters for a task.

    Parameters:
    -----------
    task_name: str
        Name of the task.
    parameters_model: type[BaseParameters]
        Parameters model for the task.
    results_model: type[BaseResult]
        Results model for the task.

    Returns:
    --------
    tuple[JobIDType, BaseParameters]
        Job ID and parameters model.

    Raises:
        ValueError: If required parameters are missing or invalid.
    """
    parser = argparse.ArgumentParser(
        description=f"Run {task_name.replace('_', ' ').title()} workflow",
    )
    # Add job_id argument
    parser.add_argument(
        '--job_id',
        required=True,
        help="The job ID",
    )

    # Build parser dynamically based on the Parameters model
    for name, field in parameters_model.model_fields.items():
        has_default = field.default != ...
        help_text = field.description or ""
        if has_default:
            help_text += f" (default: {field.default})"
        parser.add_argument(
            f'--{name}',
            required=not has_default,
            help=help_text,
            default=field.default if has_default else None
        )
    args = parser.parse_args()
    args_dict = vars(args)
    job_id = args_dict.pop('job_id')
    return job_id, parameters_model(**args_dict)


def run_task(task_pipeline: TaskWithJobIdType, parameters_model: type[BaseParameters], results_model: type[BaseResult]) -> None:
    """
    Run a task pipeline with input parameters. The task pipeline is expected to be a function that
    takes a job ID and a parameters model as input, and returns a results model.

    Parameters:
    -----------
    task_pipeline: TaskWithJobIdType
        Task pipeline function.
    parameters_model: type[BaseParameters]
        Parameters model for the task.
    results_model: type[BaseResult]
        Results model for the task.

    Returns:
    --------
    None
    """
    task_name = task_pipeline.task_name if hasattr(task_pipeline, "task_name") else task_pipeline.__name__
    logger.info(f"Running task {task_name}")
    # Parse and validate input parameters
    job_id, parameters = parse_run_parameters(task_name, parameters_model)
    # Run the task
    results = task_pipeline(job_id, parameters)
    logger.info(f"Results: {results}")


"""
Entry point for running or registering a task.
==============================================

Run: This entry point for running a task. It imports the task module specified in the TASK_MODULE
environment variable, then runs the task.

Register: This entry point for registering a task. It imports the task module specified in the
TASK_MODULE environment variable, then registers the task in Firestore.
"""

def run() -> None:
    task_module = os.environ.get("TASK_MODULE")
    if task_module is None:
        raise ValueError("TASK_MODULE environment variable not set")
    task, Parameters, Results = import_task(task_module)
    run_task(task, Parameters, Results)


def register() -> None:
    task_module = os.environ.get("TASK_MODULE")
    if task_module is None:
        raise ValueError("TASK_MODULE environment variable not set")
    task, Parameters, Results = import_task(task_module)
    register_task(task, Parameters, Results)
