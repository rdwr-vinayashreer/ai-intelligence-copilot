# Scheduler and Runtime Architecture

## Purpose

The AI Intelligence platform separates **when a run starts** from **where a run executes**.

```text
                    Scheduler Layer
                         |
              +----------+----------+
              |          |          |
             n8n      Jenkins     Cron
              |
              v
                    Runtime Layer
                         |
              +----------+----------+
              |                     |
       GitHub Actions          Future Runtime
              |
              v
                 Intelligence Core
              |
              v
             Run Contract
              |
       +------+-------+--------+
       |              |        |
    Delivery      Evaluation  Storage
```

## Current production path

```text
n8n
  -> GitHub workflow_dispatch
  -> GitHub Actions
  -> Copilot CLI
  -> AI Intelligence agent
  -> Run Contract
  -> Email
```

## Responsibilities

### Scheduler

Owns:
- schedule
- trigger
- selected profile
- correlation context

Does not own:
- research
- source verification
- briefing generation
- email rendering

### Runtime

Owns:
- execution environment
- dependency setup
- agent invocation
- evaluation
- run contract creation

Does not own:
- recurring schedules
- intelligence policy
- delivery-specific implementation

### Intelligence Core

Owns:
- research
- verification
- synthesis
- briefing generation

### Delivery

Owns:
- sending the completed briefing
- channel-specific authentication
- delivery status

## Design rule

Replacing n8n must not require rewriting the intelligence agent.

Replacing GitHub Actions must not require rewriting the intelligence agent.

Adding Teams or Slack must not require rewriting the intelligence agent.
