import sys; sys.path.append("..")
import os
import json

import asyncio
from pydantic import BaseModel

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

from app.db import get_firestore_client  # type: ignore

users = [
    {"id": "test@user.com", "tasks": ["task1"]},
]

class Parameters(BaseModel):
    name: str

class Result(BaseModel):
    message: str

tasks = [
    {
        "id": "task1",
        "name": "Hello World",
        "description": "Description for Task 1",
        "parameters_json_schema": json.dumps(Parameters.model_json_schema()),
        "result_json_schema": f"{json.dumps(Result.model_json_schema())}",
        "uri": "projects/project_id/locations/us-central1/jobs/task_1",
    }
]

async def populate_firestore():
    client = await get_firestore_client()
    for user in users:
        print("Adding user", user)
        user_id = user.pop("id")
        await client.collection("users").document(user_id).set(user)
    for task in tasks:
        print("Adding task", task)
        task_id = task.pop("id")
        await client.collection("tasks").document(task_id).set(task)

if __name__ == "__main__":
    asyncio.run(populate_firestore())
