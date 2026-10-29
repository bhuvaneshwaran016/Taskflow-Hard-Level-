# TaskFlow Hard Bug Challenge

A deliberately flawed task-management API for evaluating an AI CI failure detection and repair agent.

## Hidden challenge

The repository contains a concurrency bug in task claiming. Two workers can attempt to claim the same task concurrently. The intended invariant is:

> A task can be claimed by at most one worker, and every successful claim must be reflected consistently in the task state and audit history.

The defect is subtle: the implementation reads the task state, yields control, and only later writes the new owner. Under concurrent requests, both callers can observe the task as unclaimed and both can report success.

The agent should diagnose the root cause from failing tests, make the smallest safe fix, and verify all tests.

## Run locally

Python 3.11+ recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
```

The tests are expected to fail before repair. Do not change or delete tests to make the suite pass.

## Run the API

```powershell
uvicorn taskflow.api:app --reload
```

## Expected correct behavior

- Exactly one concurrent claimant succeeds.
- Other claimants receive a conflict response.
- The task owner and status agree with the successful response.
- The audit log contains exactly one successful claim event.
- Repeated claims after assignment do not overwrite the owner.
- Unrelated tasks remain claimable.
