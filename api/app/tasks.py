from typing import Any

from pydantic import BaseModel
from google.cloud.run_v2 import JobsAsyncClient, RunJobRequest

from app.models import TaskDetails


def _flatten_parameters(parameters: Any, prefix: str = "--") -> list[str]:
    """Convert the parameters into a flat list of strings with '--' prefix."""
    if isinstance(parameters, dict):
        flatten = []
        prefix = f"{prefix}." if prefix != "--" else prefix
        for key, value in parameters.items():
            flatten.extend(_flatten_parameters(value, f"{prefix}{key}"))
        return flatten
    elif isinstance(parameters, list) or isinstance(parameters, tuple):
        return [prefix, f"\"{parameters}\""]
    else:
        return [prefix, str(parameters)]


async def get_jobs_client() -> JobsAsyncClient:
    return JobsAsyncClient()


async def execute_task(client: JobsAsyncClient, task: TaskDetails, job_id: str, parameters: BaseModel | None) -> None:
    """Create a Cloud Run Job for a task."""
    full_job_name = task.uri

    parameters_values = {} if parameters is None else parameters.model_dump()
    parameters_values["job_id"] = job_id
    job_parameters = _flatten_parameters(parameters_values)

    # Start the Cloud Run Job
    run_request = RunJobRequest(
        name=full_job_name,  # Fully qualified job name
        overrides=RunJobRequest.Overrides(
            container_overrides=[
                RunJobRequest.Overrides.ContainerOverride(
                    args=job_parameters
                )
            ]
        )
    )
    await client.run_job(request=run_request)
