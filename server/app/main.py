from fastapi import FastAPI, Depends, Header, HTTPException
from google.cloud.firestore import AsyncClient as FirestoreClient
from google.cloud.run_v2 import JobsAsyncClient as CloudRunJobClient

from app.db import (
    get_firestore_client,
    list_user_tasks,
    user_has_access_to_task,
    user_has_access_to_job,
    get_job_status,
    get_task_details,
    create_job,
)
from app.tasks import (
    get_jobs_client,
    execute_task,
)
from app.schema_validation import (
    validate_with_model_schema,
)
from app.models import (
    Task,
    JobCreate,
    JobResult,
)

# Load variables from environment
app = FastAPI()

FirestoreClientDep = Depends(get_firestore_client)
CloudRunJobClientDep = Depends(get_jobs_client)

async def get_current_user(x_user_email: str = Header(None)):
    if not x_user_email:
        raise HTTPException(status_code=400, detail="User email header missing")
    return x_user_email


@app.get("/tasks")
async def get_tasks(x_user_email: str = Depends(get_current_user), db: FirestoreClient = FirestoreClientDep) -> list[Task]:
    """Get all the tasks for a user"""
    tasks = await list_user_tasks(db, x_user_email)
    return tasks


@app.post("/execute/{task_id}")
async def execute(task_id: str, parameters: dict | None, x_user_email: str = Depends(get_current_user), db: FirestoreClient = FirestoreClientDep, run: CloudRunJobClient = CloudRunJobClientDep) -> JobCreate:
    """Execute a task for a user, only if the user has access to it"""
    if not await user_has_access_to_task(db, x_user_email, task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    # Validate parameters
    task = await get_task_details(db, task_id)
    try:
        parameters_ = parameters or {}
        parameters_model = validate_with_model_schema(task.parameters_schema, parameters_)
    except ValueError:
        raise HTTPException(status_code=402, detail="Invalid parameters")

    # Create job in Firestore
    job_create = await create_job(
        db,
        x_user_email,
        task_id,
        parameters_model,
    )

    # Submit job to Cloud Run Job
    await execute_task(
        run,
        task,
        job_create.id,
        parameters_model,
    )
    return job_create

@app.get("/jobs/{job_id}")
async def get_job(job_id: str, x_user_email: str = Depends(get_current_user), db: FirestoreClient = FirestoreClientDep) -> JobResult:
    """Get the status of a job"""
    if not await user_has_access_to_job(db, x_user_email, job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    try:
        job_status = await get_job_status(db, job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status
