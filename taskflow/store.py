"""In-memory store for the TaskFlow demo challenge."""
from dataclasses import dataclass, field
from typing import Optional
import asyncio

@dataclass
class Task:
    task_id: int
    title: str
    status: str = "open"
    owner: Optional[str] = None

@dataclass
class Store:
    tasks: dict[int, Task] = field(default_factory=dict)
    audit: list[dict] = field(default_factory=list)
    next_id: int = 1
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def add_task(self, title: str) -> Task:
        task = Task(task_id=self.next_id, title=title)
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task

    async def claim_task(self, task_id: int, worker: str) -> tuple[bool, str]:
        # BUG: check and update are not atomic. Concurrent callers can both
        # pass the status check before either writes the owner.
        task = self.tasks.get(task_id)
        if task is None:
            return False, "not_found"
        if task.status != "open":
            return False, "already_claimed"

        # Simulates an async gap, such as a database/network operation.
        await asyncio.sleep(0)

        task.owner = worker
        task.status = "claimed"
        self.audit.append({"event": "claimed", "task_id": task_id, "worker": worker})
        return True, "claimed"
