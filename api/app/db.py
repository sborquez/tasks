from typing import TypeVar
import json

from google.cloud.firestore import AsyncClient, DocumentSnapshot
from pydantic import BaseModel

from app.models import get_timestamp, Task, UserDocument, TaskDetails, TaskDocument, JobDocument, JobCreate, JobResult
from app.config import settings

T = TypeVar("T", bound=BaseModel)

USERS_COLLECTION = "users"
TASKS_COLLECTION = "tasks"
JOBS_COLLECTION = "jobs"


def _validate_firestore_document(doc: DocumentSnapshot, model: type[T]) -> T:
    doc_dict = doc.to_dict() or {}
    doc_dict["id"] = doc.id
    return model.model_validate(doc_dict)


async def get_firestore_client() -> AsyncClient:
    if settings.FIRESTORE_EMULATOR_HOST:
        print("Using Firestore emulator")
        client = AsyncClient(
            project=settings.FIRESTORE_PROJECT_ID,
            database=settings.FIRESTORE_DATABASE,
            credentials=None,
        )
        client._emulator_host = settings.FIRESTORE_EMULATOR_HOST
        return client
    else:
        client = AsyncClient(
            project=settings.FIRESTORE_PROJECT_ID,
            database=settings.FIRESTORE_DATABASE,
        )
    return AsyncClient()


async def list_user_tasks(client: AsyncClient, user_email: str) -> list[Task]:
    # Find user
    user_ref = client.collection(USERS_COLLECTION).document(user_email)
    user_doc = await user_ref.get()
    if not user_doc.exists:
        print(f"User {user_email} not found")
        return []
    user = _validate_firestore_document(user_doc, UserDocument)

    # Get tasks
    tasks = []
    for task_id in user.tasks:
        task_ref = client.collection(TASKS_COLLECTION).document(task_id)
        task_doc = await task_ref.get()
        if not task_doc.exists:
            continue
        task = _validate_firestore_document(task_doc, TaskDocument)
        tasks.append(
            Task(
                id=task.id,
                name=task.name,
                description=task.description,
                # From json.dumps(Parameters.schema_json())
                parameters_schema=json.loads(task.parameters_json_schema),
                result_schema=json.loads(task.result_json_schema),
            )
        )
    return tasks


async def get_task_details(client: AsyncClient, task_id: str) -> TaskDetails:
    task_ref = client.collection(TASKS_COLLECTION).document(task_id)
    task_doc = await task_ref.get()
    if not task_doc.exists:
        raise ValueError(f"Task {task_id} not found")
    task = _validate_firestore_document(task_doc, TaskDocument)
    return TaskDetails(
        id=task.id,
        name=task.name,
        description=task.description,
        parameters_schema=json.loads(task.parameters_json_schema),
        result_schema=json.loads(task.result_json_schema),
        uri=task.uri,
    )

async def user_has_access_to_task(client: AsyncClient, user_email: str, task_id: str) -> bool:
    user_ref = client.collection(USERS_COLLECTION).document(user_email)
    user_doc = await user_ref.get()
    if not user_doc.exists:
        return False
    user = _validate_firestore_document(user_doc, UserDocument)
    return task_id in user.tasks


async def create_job(client: AsyncClient, user_email: str, task_id: str, parameters: BaseModel) -> JobCreate:
    # Create a job
    job_ref = client.collection(JOBS_COLLECTION).document()
    job = JobDocument(
        id=job_ref.id,
        task_id=task_id,
        user_id=user_email,
        created_at=get_timestamp(),
        parameters_json_value=parameters.model_dump_json(),
    )
    job_data = job.model_dump()
    job_data.pop("id")
    await job_ref.set(job_data)

    job_create = JobCreate(
        id=job_ref.id,
        task_id=task_id,
        status=job.status,
        created_at=job.created_at,
        parameters=parameters.model_dump(),
    )
    return job_create


async def user_has_access_to_job(client: AsyncClient, user_email: str, job_id: str) -> bool:
    job_ref = client.collection(JOBS_COLLECTION).document(job_id)
    job_doc = await job_ref.get()
    if not job_doc.exists:
        return False
    job = _validate_firestore_document(job_doc, JobDocument)
    return job.user_id == user_email


async def get_job_status(client: AsyncClient, job_id: str) -> JobResult:
    job_ref = client.collection(JOBS_COLLECTION).document(job_id)
    job_doc = await job_ref.get()
    if not job_doc.exists:
        raise ValueError(f"Job {job_id} not found")
    job = _validate_firestore_document(job_doc, JobDocument)
    return JobResult(
        job_id=job.id,
        task_id=job.task_id,
        status=job.status,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        parameters=json.loads(job.parameters_json_value) if job.parameters_json_value else None,
        result=json.loads(job.result_json_value) if job.result_json_value else None,
        error=json.loads(job.error_json_value) if job.error_json_value else None,
    )