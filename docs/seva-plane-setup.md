# Seva + Plane Setup

This runbook makes the Seva x Plane integration executable against a real Plane project.

## Product Decisions

- Workspace scope: one Plane workspace per Seva environment.
- Project scope: Seva v1 should use a dedicated Plane project.
- Assignment: Seva does not auto-assign issues to itself.
- Closure rule: Seva closes leaf issues only. Parent issues stay open until required child issues are done.
- Canonical metadata source: severity, component, and environment are modeled with labels.
- Event intake: v1 uses polling. Plane webhooks remain optional for later comment-driven or lower-latency automation.

## Bootstrap A Project

Run the bootstrap command against the target project:

```bash
python manage.py bootstrap_seva_project --workspace <workspace-slug> --project-id <project-uuid>
```

The command is idempotent and ensures:

- required Seva states: `backlog`, `ready`, `in_progress`, `blocked`, `in_review`, `done`, `cancelled`
- required issue types: `task`, `bug`, `feature`, `ops`, `follow_up`
- required label taxonomy roots and labels:
  - `severity`: `critical`, `high`, `medium`, `low`
  - `component`: `api`, `web`, `auth`, `billing`, `infra`, `docs`
  - `environment`: `prod`, `staging`, `sandbox`
- canonical issue template: `Seva Work Item`

## Service Account Path

Use a dedicated workspace-owned Seva bot for service-token execution.

Recommended flow:

1. Generate a workspace service token from the existing service-token flow.
2. The endpoint creates or reuses a dedicated Seva bot user for that workspace.
3. The service token is bound to that Seva bot, not to the human admin who requested it.
4. The endpoint keeps the Seva bot's project memberships aligned with `allowed_project_ids`.
5. Use that token for all Seva API requests with `X-Api-Key`.
6. Set `allowed_project_ids` to the dedicated Seva project UUID so the token cannot operate on unrelated projects.

Important:

- only workspace admins should manage the Seva service token
- the token secret is returned only when the token is first created
- subsequent calls should be treated as scope-update or metadata responses, not secret retrieval
- removing the human admin who created the token must not break Seva access, because the token runs as the workspace Seva bot

Seva should only operate in the bootstrapped dedicated project.

## Required API Flow

Use these endpoints for the Seva integration:

- Read project capabilities:
  - `GET /api/v1/workspaces/{slug}/projects/{project_id}/agent-context/`
- Poll project changes:
  - `GET /api/v1/workspaces/{slug}/projects/{project_id}/agent-updates/?cursor=<cursor>`
- Poll comment changes:
  - `GET /api/v1/workspaces/{slug}/projects/{project_id}/agent-comment-updates/?cursor=<cursor>`
- Read actionable work:
  - `GET /api/v1/workspaces/{slug}/projects/{project_id}/agent-ready-work-items/`
- Read a single work item with dependency context:
  - `GET /api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/agent-context/`
- Create or update work items:
  - `POST /api/v1/workspaces/{slug}/projects/{project_id}/work-items/`
  - `PATCH /api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/`
- Add comments:
  - `POST /api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/comments/`
- Create or inspect dependency links:
  - `GET /api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/relations/`
  - `POST /api/v1/workspaces/{slug}/projects/{project_id}/work-items/{issue_id}/relations/`

## Polling Contract

`agent-updates` returns work items ordered by `updated_at` and `id`.

`agent-comment-updates` returns comments ordered by `updated_at` and `id` so Seva can react to review feedback and operator notes even when the parent issue timestamp does not change.

- request cursor format: `<iso-timestamp>::<issue-uuid>`
- response field: `polling.next_cursor`
- dedupe rule: always replay from the last `next_cursor` only after the previous batch is fully processed
- default interval: 60 seconds
- recommended v1 behavior: poll both endpoints on the same interval and re-fetch the issue context for any comment update results

## Verified Agent Flow

The supported v1 flow is:

1. Read `ready` work from `agent-ready-work-items`.
2. Move the issue to `in_progress` through the public work-item patch endpoint.
3. Add a progress comment.
4. Create a linked `follow_up` issue when new work is discovered.
5. Link the original issue to the follow-up with `blocked_by` and move the original issue to `blocked`.
6. Complete the follow-up issue.
7. Add a completion note and move the original issue to `done`.

## Misconfiguration Detection

`agent-context` returns `seva_configuration` with:

- `is_ready`
- `missing.states`
- `missing.issue_types`
- `missing.labels`
- `missing.issue_template`

Seva should refuse to operate when `is_ready` is `false`.
