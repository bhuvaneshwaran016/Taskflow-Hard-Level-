"""Minimal API for the TaskFlow concurrency challenge."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from taskflow.store import Store

app = FastAPI(title="TaskFlow Hard Bug Challenge")
store = Store()

class CreateTask(BaseModel):
    title: str = Field(min_length=1, max_length=200)

class ClaimTask(BaseModel):
    worker: str = Field(min_length=1, max_length=80)

@app.post("/tasks", status_code=201)
async def create_task(body: CreateTask):
    task = store.add_task(body.title)
    return {"task_id": task.task_id, "title": task.title, "status": task.status, "owner": task.owner}

@app.post("/tasks/{task_id}/claim")
async def claim_task(task_id: int, body: ClaimTask):
    ok, reason = await store.claim_task(task_id, body.worker)
    if not ok:
        if reason == "not_found":
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=409, detail="Task already claimed")
    return {"task_id": task_id, "owner": body.worker, "status": "claimed"}

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    task = store.tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task.task_id, "title": task.title, "status": task.status, "owner": task.owner}

@app.get("/audit")
async def get_audit():
    return list(store.audit)
