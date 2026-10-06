
---

## 3. Add `delivery/gmail/README.md`

```markdown
# Gmail Delivery Adapter

## Purpose

The Gmail adapter delivers a completed AI Intelligence briefing through Gmail
SMTP.

## Required Secrets

- `GMAIL_USERNAME`
- `GMAIL_APP_PASSWORD`
- `BRIEFING_RECIPIENT`

## Input

The adapter receives:

- `run_id`
- `profile`
- briefing content
- recipient

## Output

The delivery operation reports:

- run ID
- delivery channel
- delivery status

## Security

Credentials must never be:

- committed to the repository
- printed in logs
- embedded in configuration files
- included in briefing artifacts

## Current Runtime

The Gmail implementation currently runs inside GitHub Actions.

It may later be extracted into a standalone delivery service when multiple
execution runtimes or delivery channels require it.