from enum import StrEnum
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from tasks.types import BaseResult


def get_timestamp() -> str:
    """Get the current timestamp in ISO format

    Returns:
    --------
    str
        Current timestamp in ISO format
    """
    return datetime.now(timezone.utc).isoformat()


"""
Tasks
-----

Tasks are the main building blocks of the system. They are composed of steps that are executed in sequence.
"""

class RegisterTask(BaseModel):
    """Task registration data"""

    name: str = Field(
        description="The name of the task",
    )

    description: str = Field(
        description="The description of the task",
    )

    uri: list[str] = Field(
        description="The URI of the task. It can be a Cloud Run job name or a local function",
    )

    parameters_json_schema: dict = Field(
        description="The JSON schema of the parameters",
    )

    result_json_schema: dict = Field(
        description="The JSON schema of the result",
    )


"""
Jobs
----

Jobs are the execution of a task with specific parameters. They have a status and a result.
"""

class JobStatus(StrEnum):
    """The status of a job"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobProgressStep(BaseModel):
    """A step in the progress of a job"""
    name: str
    description: str
    started_at: str = Field(description="The start date of the step, in ISO format")
    completed_at: str = Field(description="The completion date of the step, in ISO format")
    status: JobStatus = Field(description="The status of the step", default=JobStatus.CREATED)


class JobProgress(BaseModel):
    """Progress information for a job"""
    steps: list[JobProgressStep] = Field(description="The detailed steps")


class JobError(BaseModel):
    """Error information for a job"""
    code: str
    message: str
    additional_info: dict | None = None


class CreateJob(BaseModel):
    """Job creation data"""


    task_id: str = Field(
        description="The task document ID",
    )

    parameters_json_value: str = Field(
        description="The parameters of the job in JSON format",
    )

    user_id: None = Field(
        description="The user email, which is the Firestore document ID",
        default=None,
    )

    status: JobStatus = Field(
        description="The current status of the job",
        default=JobStatus.CREATED,
    )

    created_at: str = Field(
        description="The creation date of the job in ISO format",
        default_factory=get_timestamp,
    )

    completed_at: None = Field(
        description="The completion date of the job in ISO format",
        default=None,
    )

    error_json_value: None = Field(
        description="The error of the job in JSON format",
        default=None,
    )

    result_json_value: None = Field(
        description="The result of the job in JSON format",
        default=None,
    )

    progress: None = Field(
        description="The current detailed status of the job. It has the step-by-step progress.",
        default=None,
    )


class StartJob(BaseModel):
    """Job starting data to update the job status"""

    status: JobStatus = Field(
        description="The current status of the job",
        default=JobStatus.RUNNING,
    )
    started_at: str = Field(
        description="The starting date of the job in ISO format",
        default_factory=get_timestamp,
    )

    progress: JobProgress = Field(
        description="The current detailed status of the job. It has the step-by-step progress.",
        default=JobProgress(steps=[]),
    )


class FailJob(BaseModel):
    """Job ending data to update the job status"""

    status: JobStatus = Field(
        description="The current status of the job",
        default=JobStatus.FAILED,
    )

    error: JobError = Field(
        description="The error of the job",
    )

    result: None = Field(
        description="The result of the job",
        default=None,
    )

    completed_at: str = Field(
        description="The completion date of the job in ISO format",
        default_factory=get_timestamp,
    )


class FinishJob(BaseModel):
    """Job ending data to update the job status"""

    status: JobStatus = Field(
        description="The current status of the job",
        default=JobStatus.COMPLETED,
    )

    result: BaseResult = Field(
        description="The result of the job",
    )

    error: None = Field(
        description="The error of the job",
        default=None,
    )

    completed_at: str = Field(
        description="The completion date of the job in ISO format",
        default_factory=get_timestamp,
    )


class StartJobStep(BaseModel):
    """Job step for the job progress updatte. This is for starting data to update the job status"""

    name: str = Field(
        description="The name of the step",
    )
    description: str = Field(
        description="The description of the step",
    )
    status: JobStatus = Field(
        description="The current status of the step",
        default=JobStatus.RUNNING,
    )
    started_at: str = Field(
        description="The starting date of the step in ISO format",
        default_factory=get_timestamp,
    )
    completed_at: None = Field(
        description="The completion date of the step in ISO format",
        default=None,
    )


class FailJobStep(BaseModel):
    """Job step for the job progress updatte. This is for failure data to update the job status"""

    status: JobStatus = Field(
        description="The current status of the step",
        default=JobStatus.FAILED,
    )
    completed_at: str = Field(
        description="The completion date of the step in ISO format",
        default_factory=get_timestamp,
    )


class FinishJobStep(BaseModel):
    """Job step for the job progress updatte. This is for ending data to update the job status"""

    status: JobStatus = Field(
        description="The current status of the step",
        default=JobStatus.COMPLETED,
    )
    completed_at: str = Field(
        description="The completion date of the step in ISO format",
        default_factory=get_timestamp,
    )
