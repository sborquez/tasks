from enum import StrEnum
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from pydantic.json_schema import JsonSchemaValue


def get_timestamp() -> str:
    """Get the current timestamp in ISO format

    Returns:
    --------
    str
        Current timestamp in ISO format
    """
    return datetime.now(timezone.utc).isoformat()

"""
Users
-----

Users are the main actors in the system. They have access to tasks and can submit jobs.
"""
class UserDocument(BaseModel):
    """
    User document in Firestore, with the list of tasks the user has access to.
    """
    id: str = Field(description="User email, the Firestore document ID")
    tasks: list[str] = Field(description="List of task IDs the user has access to")



"""
Jobs
----

Jobs are the execution of a task with specific parameters. They have a status and a result.
"""

class JobStatus(StrEnum):
    """The status of a job"""
    CREATED = "created"
    PENDING = "pending"
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


class JobDocument(BaseModel):
    """Job document in Firestore, a job is the execution of a task by a user. It has information
    about the status, the result and the parameters.
    """

    id: str = Field(description="The Firestore document ID")
    task_id: str = Field(description="The task document ID")
    user_id: str = Field(description="The user email, which is the Firestore document ID")

    status: JobStatus = Field(
        description="The current status of the job",
        default=JobStatus.CREATED,
    )
    progress: JobProgress | None = Field(
        description="The current detailed status of the job. It has the step-by-step progress.",
        default=None,
    )

    created_at: str = Field(
        description="The creation date of the job, in ISO format",
        default_factory=get_timestamp,
    )
    started_at: str | None = Field(
        description="The start date of the job, in ISO format",
        default=None,
    )
    completed_at: str | None = Field(
        description="The completion date of the job, in ISO format",
        default=None,
    )

    parameters_json_value: str | None = Field(
        description="The parameters of the job in JSON format",
        default=None,
    )
    result_json_value: str | None = Field(
        description="The result of the job in JSON format",
        default=None,
    )

    error_json_value: str | None = Field(
        description="The error of the job in JSON format",
        default=None,
    )


class JobCreate(BaseModel):
    """Job creation response, with the ID, the task ID, the status, the creation date and the
    parameters.
    """
    id: str = Field(description="The Firestore document ID")
    task_id: str = Field(description="The task document ID")

    status: JobStatus = Field(
        description="The current status of the job",
        default=JobStatus.CREATED,
    )
    created_at: str = Field(description="The creation date of the job in ISO format")

    parameters: dict | None = Field(description="The parameters of the job", default=None)


class JobResult(BaseModel):
    """Job result response, with the ID, the task ID, the status, the creation date, the start date,
    the completion date, the parameters, the result and the error.
    """
    job_id: str = Field(description="The Firestore document ID")
    task_id: str = Field(description="The task document ID")

    status: JobStatus = Field(description="The current status of the job")
    created_at: str = Field(description="The creation date of the job in ISO format")
    started_at: str | None = Field(description="The start date of the job in ISO format")
    completed_at: str | None = Field(description="The completion date of the job in ISO format")

    parameters: dict | None = Field(description="The parameters of the job", default=None)
    result: dict | None = Field(description="The result of the job", default=None)
    error: JobError | None = Field(description="The error of the job", default=None)


"""
Tasks
-----

Tasks are the main building blocks of the system. They define the work that needs to be done, what
parameters are needed, and the expected results.
"""

class TaskDocument(BaseModel):
    """Task document in Firestore, a task is the definition of the work to be done. It has
    information about the name, the description, the parameters schema, the result schema and the
    Cloud Run job name.
    """
    id: str = Field(description="The Firestore document ID")

    name: str = Field(description="The name of the task")
    description: str = Field(description="The description of the task")
    parameters_json_schema: str = Field(description="The JSON schema of the parameters. Generated by Pydantic BaseModel.model_json_schema()")
    result_json_schema: str = Field(description="The JSON schema of the result. Generated by Pydantic BaseModel.model_json_schema()")

    uri: str = Field(description="Identifier to the task location. e.g. the Cloud Run job name. With the format 'projects/{project_id}/locations/{location}/jobs/{job_id}'")


class Task(BaseModel):
    """Task Response, with the name, the description, the parameters schema and the result schema.
    """
    name: str = Field(description="The name of the task")
    description: str = Field(description="The description of the task")

    # pydantic schema
    parameters_schema: JsonSchemaValue = Field(description="The JSON schema of the parameters, generated by Pydantic BaseModel.model_json_schema()")
    result_schema: JsonSchemaValue = Field(description="The JSON schema of the result, generated by Pydantic BaseModel.model_json_schema()")


class TaskDetails(Task):
    """Task details with the ID and the Cloud Run job name"""
    id: str = Field(description="The Firestore document ID")

    uri: str = Field(description="Identifier to the task location. e.g. the Cloud Run job name. With the format 'projects/{project_id}/locations/{location}/jobs/{job_id}'")
