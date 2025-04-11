import argparse
import importlib
import os
import json

from pydantic import BaseModel, Field
from fastapi import FastAPI

from tasks.types import TaskWithJobIdType, JobIDType, BaseParameters, BaseResult
from tasks.db import create_task, get_firestore_client
from tasks.utils import get_logger, normalize_string
from tasks.config import settings


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
        required=False,
        help="Identifier to the task location. e.g. the Cloud Run job name with the format 'projects/{project_id}/locations/{location}/jobs/{job_id}'",
        default=None,
    )
    args = parser.parse_args()
    task_uri = args.task_uri
    if task_uri is None:
        project_id = settings.TASK_PROJECT_ID
        region = settings.TASK_REGION
        job_name = settings.TASK_JOB_NAME
        if any([project_id is None, region is None, job_name is None]):
            raise ValueError("TASK_PROJECT_ID, TASK_REGION, and TASK_JOB_NAME must be set in the environment or passed as arguments")
        task_uri = f"projects/{project_id}/locations/{region}/jobs/{job_name}"
    return task_uri


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



def build_request_parameters(parameters_model: type[BaseParameters]) -> type:
    """
    Define a task BaseParameters model for a endpoint.

    Parameters:
    -----------
    parameters_model: type[BaseParameters]
        Parameters model for the task.

    Returns:
    --------
    type
        A BaseParameters model class for an endpoint.
    """

    class EndpointParameters(BaseModel):
        """
        A class representing the parameters for a task.
        Inherits from the provided parameters_model.
        """
        job_id: JobIDType = Field(description="The job ID")

    class TaskEndpointBody(BaseModel):
        """
        A class representing the request parameters for a task.
        Inherits from the provided parameters_model.
        """
        instances: list[parameters_model] = Field(  # type: ignore
            description="List of instances to be processed by the task.",
        )
        parameters: EndpointParameters

    return TaskEndpointBody


def serve_task(task_pipeline: TaskWithJobIdType, parameters_model: type[BaseParameters], results_model: type[BaseResult]) -> None:
    """
    Create and serve a FastAPI app for the task pipeline.

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
    logger.info(f"Serving task {task_name}")
    # Parse and validate input parameters
    TaskEndpointBody = build_request_parameters(parameters_model)

    port = int(os.environ.get("AIP_HTTP_PORT", settings.SERVER_PORT))
    health_endpoint = os.environ.get("AIP_HEALTH_ROUTE", settings.SERVER_HEALTH_ENDPOINT)
    predict_endpoint = os.environ.get("AIP_PREDICT_ROUTE", settings.SERVER_PREDICT_ENDPOINT)

    class HealthCheckResponse(BaseModel):
        """
        A class representing the health check response.
        """
        status: str = Field(description="Health check status")
        task_name: str = Field(description="Task name")
        task_id: str = Field(description="Task ID")
        task_description: str = Field(description="Task description")


    class TaskEndpointResponse(BaseModel):
        """
        A class representing the response for a task endpoint.
        """
        predictions: list[results_model] = Field(  # type: ignore
            description="List of instances processed by the task.",
        )

    # Serve the task
    app = FastAPI(
        title=f"{task_name.replace('_', ' ').title()} API",
    )

    @app.get(
        path=health_endpoint,
        description="Health check endpoint",
    )
    async def health_check() -> HealthCheckResponse:
        return HealthCheckResponse(
            status="ok",
            task_name=task_name,
            task_id=task_pipeline.task_id,
            task_description=task_pipeline.task_description,
        )

    @app.post(
        path=predict_endpoint,
        description=f"Run {task_name.replace('_', ' ').title()} workflow",
    )
    async def endpoint(parameters: TaskEndpointBody) -> TaskEndpointResponse:  # type: ignore
        job_id = parameters.parameters.job_id
        # Convert instances to a list of parameters
        all_results = []
        for instance in parameters.instances:
            all_results.append(
                task_pipeline(job_id, instance)
            )
        return TaskEndpointResponse(predictions=all_results)

    # Run the FastAPI app
    import uvicorn
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=port,
        log_level=settings.SERVER_LOG_LEVEL,
    )


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


def serve() -> None:
    """
    Serve the task pipeline. This is a placeholder function that can be used to serve the task
    pipeline using a FastAPI web server.
    """
    task_module = os.environ.get("TASK_MODULE")
    if task_module is None:
        raise ValueError("TASK_MODULE environment variable not set")
    task, Parameters, Results = import_task(task_module)
    serve_task(task, Parameters, Results)
