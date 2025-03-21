from dataclasses import dataclass
import json
from typing import TypeVar

from google.cloud.firestore import Client
from pydantic import BaseModel

from tasks.types import BaseParameters
from tasks.config import settings
from tasks.models import (
    JobStatus,
    CreateJob,
    StartJob,
    FailJob,
    FinishJob,
    StartJobStep,
    FailJobStep,
    FinishJobStep,
)
from tasks.utils import get_logger

T = TypeVar("T", bound=BaseModel)

TASKS_COLLECTION = "tasks"
JOBS_COLLECTION = "jobs"

logger = get_logger(__name__)


@dataclass(frozen=True)
class _Context:
    """Context for the task execution, with the job ID and the Firestore client."""
    job_id: str
    task_id: str
    parameters: BaseParameters
    db: Client


def setup_context(job_id: str, task_id: str, parameters: BaseParameters) -> _Context:
    """Setup the context for the task execution, with the job ID and the Firestore client."""
    ctx = _Context(
        job_id=job_id,
        task_id=task_id,
        parameters=parameters.model_copy(),
        db=get_firestore_client(),
    )
    return _get_context(ctx)


def _get_context(ctx: _Context | None = None) -> _Context:
    if ctx is not None:
        _get_context.ctx = ctx
    elif not hasattr(_get_context, "ctx") or _get_context.ctx is None:
        raise RuntimeError("Context not set")
    return _get_context.ctx


def get_context() -> _Context:
    """Get the context for the task execution."""
    return _get_context()


def get_firestore_client() -> Client:
    if settings.FIRESTORE_EMULATOR_HOST:
        logger.debug("Using Firestore emulator")
        client = Client(
            project=settings.FIRESTORE_PROJECT_ID,
            credentials=None,
        )
        client._emulator_host = settings.FIRESTORE_EMULATOR_HOST
    else:
        logger.debug("Using Firestore")
        client = Client()
    return client


def create_task(client: Client, task_id: str, task_name: str, task_description: str, parameters_json_schema: str, result_json_schema: str, uri: str) -> None:
    """Create a task in Firestore."""
    logger.info(f"Creating task with id: {task_id}")
    logger.info(f"Task name: {task_name}")
    logger.info(f"Task description: {task_description}")
    logger.info(f"Task parameters JSON schema: {parameters_json_schema}")
    logger.info(f"Task result JSON schema: {result_json_schema}")
    logger.info(f"Task URI: {uri}")
    client.collection(TASKS_COLLECTION).document(task_id).set(
        {
            "name": task_name,
            "description": task_description,
            "parameters_json_schema": parameters_json_schema,
            "result_json_schema": result_json_schema,
            "uri": uri,
        }
    )


def create_or_check_job(client: Client, job_id: str, task_id: str, parameters: BaseParameters) -> bool:
    """Check if a job with the given ID exists in Firestore, otherwise create it."""
    job_ref = client.collection(JOBS_COLLECTION).document(job_id)
    job_doc = job_ref.get()
    if job_doc.exists:
        logger.info(f"Job {job_id} already exists")
        logger.info(f"Job {job_id} status: {job_doc}")
        curr_status = job_doc.to_dict().get("status", JobStatus.FAILED)
        if curr_status != JobStatus.CREATED:
            logger.error(f"Job {job_id} is not in \"created\" status, but in \"{curr_status}\"")
            raise ValueError(f"Job {job_id} is not in \"created\" status, but in \"{curr_status}\"")
        return True
    logger.info(f"Creating job {job_id}")
    job_ref.set(
        CreateJob(
            task_id=task_id,
            parameters_json_value=parameters.model_dump_json(),
        ).model_dump()
    )
    exists = False
    return exists


def update_job_status(client: Client, job_id: str, job_update: StartJob | FailJob | FinishJob) -> None:
    """Update the status of a job in Firestore."""
    logger.debug(f"Updating job {job_id} with {job_update}")
    job_ref = client.collection(JOBS_COLLECTION).document(job_id)
    if not job_ref.get().exists:
        raise ValueError(f"Job {job_id} not found")
    if isinstance(job_update, StartJob):
        job_ref.update(
            {
                "status": job_update.status,
                "started_at": job_update.started_at,
            }
        )
    elif isinstance(job_update, FailJob) or isinstance(job_update, FinishJob):
        job_ref.update(
            {
                "status": job_update.status,
                "completed_at": job_update.completed_at,
                "result_json_value": job_update.result.model_dump_json() if job_update.result else None,
                "error_json_value": job_update.error.model_dump_json() if job_update.error else None,
            }
        )
    else:
        raise ValueError(f"Invalid job update: {job_update}")


def update_job_step_status(client: Client, job_id: str, job_step_update: StartJobStep | FailJobStep | FinishJobStep) -> None:
    """Update the status of a job step in Firestore."""
    logger.debug(f"Updating job {job_id} step with {job_step_update}")
    job_ref = client.collection(JOBS_COLLECTION).document(job_id)
    if not job_ref.get().exists:
        raise ValueError(f"Job {job_id} not found")

    if isinstance(job_step_update, StartJobStep):
        progress = job_ref.get().to_dict().get("progress") or {}
        steps = progress.get("steps", [])
        steps.append(
            {
                "name": job_step_update.name,
                "description": job_step_update.description,
                "status": job_step_update.status,
                "started_at": job_step_update.started_at,
            }
        )
        job_ref.update(
            {
                "progress": {
                    "steps": steps
                }
            }
        )
    elif isinstance(job_step_update, FailJobStep) or isinstance(job_step_update, FinishJobStep):
        steps = job_ref.get().to_dict()["progress"]["steps"]
        steps[-1].update(
            {
                "status": job_step_update.status,
                "completed_at": job_step_update.completed_at,
            }
        )
        job_ref.update({
            "progress": {
                "steps": steps
            }
        })
    else:
        raise ValueError(f"Invalid job step update: {job_step_update}")
