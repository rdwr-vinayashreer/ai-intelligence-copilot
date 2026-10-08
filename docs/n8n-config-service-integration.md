# n8n → Configuration Service Integration

## Purpose

n8n is responsible for recurring scheduling and triggering AI Intelligence
runs. The Configuration Service is the source of truth for employee
preferences and schedules.

## Flow

Schedule Trigger
    ↓
GET /api/v1/scheduler/due-users
    ↓
Loop over due users
    ↓
GitHub workflow_dispatch
    ↓
POST /api/v1/scheduler/dispatches

## Authentication

Scheduler endpoints require:

X-Scheduler-Key: <scheduler secret>

The scheduler secret must be stored in the n8n credential/secret store.

It must never be committed to GitHub, stored in employee configuration,
or included in workflow source code.

## GET /api/v1/scheduler/due-users

Returns users whose configured local briefing time matches the current
minute and whose scheduled occurrence has not already been dispatched.

Example:

{
  "status": "success",
  "checked_at": "2026-10-08T08:43:15.772344+00:00",
  "users": [
    {
      "user_id": "employee-005",
      "user_config": {
        "user_id": "employee-005",
        "profile": "general-ai",
        "topics": [
          "models",
          "agentic_ai",
          "ai_research"
        ],
        "schedule": {
          "timezone": "Asia/Kolkata",
          "time": "14:13"
        },
        "delivery": {
          "channel": "email",
          "destination": "employee@example.com"
        }
      },
      "scheduled_at": "2026-10-08T14:13:00+0530",
      "correlation_id": "AIINT-employee-005-20261008-1413"
    }
  ],
  "count": 1
}

## GitHub workflow_dispatch

For each due user, n8n sends:

{
  "ref": "main",
  "inputs": {
    "user_config": "<user_config>",
    "trigger": "scheduled",
    "trigger_source": "n8n-scheduler",
    "correlation_id": "<correlation_id>"
  }
}

## POST /api/v1/scheduler/dispatches

After a successful GitHub dispatch, n8n records:

{
  "user_id": "<user_id>",
  "scheduled_at": "<scheduled_at>",
  "correlation_id": "<correlation_id>"
}

The Configuration Service records this occurrence using:

(user_id, scheduled_at)

as the idempotency key.

## Failure handling

If GitHub workflow_dispatch fails:

- Do not record the dispatch.
- The employee remains due.
- The next scheduler execution can retry the dispatch.

If dispatch succeeds but recording the dispatch fails:

- The occurrence may be rediscovered.
- GitHub workflow correlation_id must remain stable.
- Duplicate protection must therefore exist in the runtime/delivery layer.

## Responsibilities

### Configuration Service

- Store employee preferences.
- Validate configuration.
- Determine due users.
- Generate stable correlation IDs.
- Record scheduler dispatches.

### n8n

- Execute recurring scheduler trigger.
- Authenticate to Configuration Service.
- Request due users.
- Dispatch GitHub workflows.
- Record successful dispatches.

### GitHub Actions

- Execute the AI Intelligence runtime.
- Resolve the supplied user configuration.
- Produce and deliver the briefing.
- Record runtime outcome.

### PostgreSQL

- Persist employee preferences.
- Persist scheduler dispatch state.

### Source of truth

Employee configuration:

PostgreSQL

Not:

- GitHub user YAML files
- n8n workflow state
- local files