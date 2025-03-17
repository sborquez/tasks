import sys; sys.path.append("..")
import os
import json

import asyncio
from pydantic import BaseModel

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

from app.db import get_firestore_client

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
        "parameters_json_schema": f"{json.dumps(Parameters.model_json_schema(mode='serialization'))}",
        "result_json_schema": f"{json.dumps(Result.model_json_schema(mode='serialization'))}",
        "cloud_run_job_name": "task1-job",
    }
]

async def populate_firestore():
    client = await get_firestore_client()
    for user in users:
        print("Adding user", user)
        await client.collection("users").document(user["id"]).set(user)
    for task in tasks:
        print("Adding task", task)
        await client.collection("tasks").document(task["id"]).set(task)

if __name__ == "__main__":
    asyncio.run(populate_firestore())
