# AI Intelligence User Onboarding

Employees do not need to modify the AI Intelligence workflow.

## Onboarding flow

1. Open GitHub Actions.
2. Select `Onboard AI Intelligence User`.
3. Click `Run workflow`.
4. Enter:
   - User ID
   - Intelligence profile
   - Topics
   - Timezone
   - Daily briefing time
   - Email destination
5. The onboarding workflow validates the configuration.
6. A pull request is created automatically.
7. An authorized reviewer reviews and merges the pull request.
8. The scheduler automatically discovers the new user.
9. The existing AI Intelligence workflow executes the briefing.
10. The configured delivery channel receives the briefing.

## Important architecture rule

Employees never modify the AI Intelligence execution workflow.

User-specific settings belong to the configuration layer.

The execution runtime is shared by all users.

## Configuration layers

```text
User
  ↓
User Configuration
  ↓
Scheduler Registry
  ↓
Generated Scheduler Manifest
  ↓
n8n Scheduler
  ↓
GitHub Actions Runtime
  ↓
AI Intelligence Agent
  ↓
User Delivery
## Supported profiles

- general-ai
- ai-engineering

## Current delivery

- email

## Security

Authentication credentials must never be stored in user configuration.

Email destinations are configuration data and should be handled according to company data-handling requirements.
