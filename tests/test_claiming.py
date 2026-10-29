import asyncio
import pytest
from taskflow.store import Store

@pytest.mark.asyncio
async def test_only_one_worker_can_claim_task_concurrently():
    store = Store()
    task = store.add_task("Deploy release")

    results = await asyncio.gather(
        store.claim_task(task.task_id, "worker-A"),
        store.claim_task(task.task_id, "worker-B"),
    )

    successes = [result for result in results if result[0]]
    assert len(successes) == 1, f"Expected exactly one winner, got: {results}"

    task_after = store.tasks[task.task_id]
    assert task_after.owner in {"worker-A", "worker-B"}
    assert task_after.status == "claimed"
    assert len(store.audit) == 1
    assert store.audit[0]["worker"] == task_after.owner

@pytest.mark.asyncio
async def test_second_claim_does_not_overwrite_first_owner():
    store = Store()
    task = store.add_task("Build package")

    first = await store.claim_task(task.task_id, "alice")
    second = await store.claim_task(task.task_id, "bob")

    assert first == (True, "claimed")
    assert second == (False, "already_claimed")
    assert store.tasks[task.task_id].owner == "alice"
    assert len(store.audit) == 1

@pytest.mark.asyncio
async def test_missing_task_is_not_claimable():
    store = Store()
    result = await store.claim_task(999, "worker-A")
    assert result == (False, "not_found")
    assert store.audit == []

@pytest.mark.asyncio
async def test_different_tasks_can_be_claimed_independently():
    store = Store()
    one = store.add_task("Task one")
    two = store.add_task("Task two")

    results = await asyncio.gather(
        store.claim_task(one.task_id, "worker-A"),
        store.claim_task(two.task_id, "worker-B"),
    )

    assert all(result[0] for result in results)
    assert store.tasks[one.task_id].owner == "worker-A"
    assert store.tasks[two.task_id].owner == "worker-B"
    assert len(store.audit) == 2
