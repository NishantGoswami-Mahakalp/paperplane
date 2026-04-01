# Seva + Plane Requirements

This document defines the minimum product and integration requirements needed for a Paperplane agent to implement a seamless Seva integration with Plane.

The implemented v1 setup and decision record live in `docs/seva-plane-setup.md`.

## Goal

Seva should be able to use Plane as its task system without manual translation, brittle heuristics, or ambiguous workflow state.

At a minimum, Seva must be able to:

- read ready work from Plane
- understand issue priority, status, ownership, and dependencies
- create new issues for discovered work
- update issue state as work progresses
- close work with clear completion notes
- surface blockers and handoff context

## Scope

This requirements set covers:

- Plane workspace and project setup
- issue schema and workflow conventions
- API and webhook access
- agent permissions and behavior boundaries
- success criteria for a production-ready integration

This does not cover:

- Seva UI design
- custom Plane plugin development unless required later
- billing or procurement for Plane itself

## Source Of Truth

Plane must be the single source of truth for Seva-managed work in the selected project.

Requirements:

- No parallel markdown TODO systems for the same work
- No duplicate issue tracking across another tool for the same execution path
- All follow-up work discovered by Seva must be created in Plane
- Status in Plane must reflect actual work state, not a delayed summary

## Workspace Setup

Plane must provide a dedicated workspace or clearly isolated project for Seva-managed work.

Required setup:

- one Plane workspace available to Seva
- at least one project where Seva is allowed to operate
- stable project identifiers available via API
- stable environment separation if multiple environments exist, such as `prod`, `staging`, or `sandbox`

Recommended setup:

- a dedicated Seva project for platform work, or
- a constrained list of approved projects Seva may act in

## Required Issue Fields

Every issue Seva touches must expose the following fields through the Plane API.

Required:

- `id`
- `title`
- `description`
- `state` or `status`
- `priority`
- `assignee`
- `labels`
- `project`
- `created_at`
- `updated_at`

Strongly recommended:

- `estimate`
- `start_date`
- `target_date`
- `parent`
- `sub-issues` or linked issues
- `blocked_by` or dependency links
- `completed_at`

## Required Workflow States

Plane must define a workflow that Seva can map cleanly to execution behavior.

Required states:

- `backlog`
- `ready`
- `in_progress`
- `blocked`
- `in_review` or `needs_review`
- `done`
- `cancelled`

State rules:

- `ready` means unblocked and actionable now
- `in_progress` means actively owned by one actor
- `blocked` means external dependency prevents progress
- `done` means acceptance criteria are met
- `cancelled` means intentionally abandoned, not silently dropped

## Required Issue Types

Plane must support a small, stable taxonomy that Seva can reason about.

Required issue types:

- `bug`
- `feature`
- `task`
- `ops`
- `follow_up`

Optional but useful:

- `epic`
- `research`
- `incident`

## Required Templates

Issues intended for Seva must follow a structured description template.

Minimum template sections:

- `Why`
- `What`
- `Acceptance Criteria`
- `Dependencies`
- `Notes / Handoff`

Suggested format:

```md
## Why

Why this work matters.

## What

What must be changed.

## Acceptance Criteria

- condition 1
- condition 2

## Dependencies

- blocking issue or external dependency

## Notes

Relevant context, links, or constraints.
```

## Labels And Components

Seva needs a predictable classification scheme.

Required conventions:

- stable labels for severity
- stable labels for domain or component
- stable labels for environment when relevant

Recommended label sets:

- severity: `critical`, `high`, `medium`, `low`
- type: `bug`, `feature`, `task`, `ops`
- component: `api`, `web`, `auth`, `billing`, `infra`, `docs`
- environment: `prod`, `staging`, `sandbox`

Rules:

- avoid free-form synonyms for the same meaning
- do not use multiple competing labels for one concept
- document the allowed label vocabulary

## Dependencies And Hierarchy

Seva must be able to understand execution order and discovered work.

Required capabilities:

- parent-child relationships or sub-issues
- blocker relationships
- ability to create linked follow-up issues

Behavior rules:

- Seva must not close a parent issue while required child issues remain open
- newly discovered work must be linked back to the originating issue
- blocked work must point to the actual blocking issue or external dependency

## Permissions Model

Seva must use a dedicated service account or API token with explicit permissions.

Minimum required permissions:

- read projects, states, labels, issues, comments
- create issues
- update issue fields
- add comments
- transition issue status
- close issues

Recommended restrictions:

- no admin or workspace configuration access
- no user-management permissions
- no permission to modify workflow definitions unless explicitly intended
- project-scoped credentials where possible

## API Requirements

Plane must expose stable API access for the following actions:

- list accessible projects
- list states for a project
- list labels and members
- query ready issues
- fetch full issue details
- create issue
- update issue
- add comment
- list linked issues or dependencies
- close or transition issue

API requirements:

- token-based authentication
- documented rate limits
- stable pagination behavior
- predictable error responses
- timestamps in a machine-friendly format

## Webhook Requirements

Webhooks are strongly recommended for seamlessness.

Useful webhook events:

- issue created
- issue updated
- issue transitioned
- comment added
- issue assigned
- issue completed

Webhook requirements:

- signed payloads or another verification method
- retry behavior for transient failures
- enough payload data to avoid immediate re-fetch in simple cases

## Agent Operating Rules

Seva should follow these behavioral constraints when working against Plane.

Required rules:

- only pick issues in `ready`
- move an issue to `in_progress` when work starts
- comment when blocked, including the reason
- create linked follow-up issues when new work is discovered
- close only when acceptance criteria are met
- add concise completion notes before closing

Recommended rules:

- prefer one active issue at a time per agent session
- avoid reassigning human-owned work without explicit permission
- avoid closing issues with unresolved blocker links

## Acceptance Criteria For A Seamless Integration

The Plane setup is sufficient when all of the following are true:

1. Seva can fetch a list of actionable `ready` issues without manual filtering.
2. Seva can understand issue type, priority, owner, and dependencies from API data alone.
3. Seva can claim work by transitioning the issue to `in_progress`.
4. Seva can create discovered follow-up issues with correct links back to the source issue.
5. Seva can mark blocked work with explicit blocker context.
6. Seva can close completed work with a summary comment.
7. Humans reviewing Plane can understand Seva's work history without outside context.

## Recommended Pilot Test

Before calling the integration production-ready, validate these three flows:

1. New work intake
   Seva reads a `ready` issue, moves it to `in_progress`, and comments progress.

2. Discovered blocker
   Seva creates a linked follow-up issue, moves the original issue to `blocked`, and records the dependency.

3. Successful completion
   Seva completes the task, adds a completion note, and transitions the issue to `done`.

## Open Decisions

These should be decided before implementation starts:

- Which Plane projects Seva may operate in
- Whether Seva may auto-assign issues to itself
- Whether Seva may close parent issues or only leaf issues
- Whether comments should follow a required format
- Whether labels or custom fields are the canonical place for component and severity

## Implementation Summary

For Paperplane agent work, assume the integration is ready only if:

- Plane provides stable project-scoped API access
- issue states and labels are standardized
- issue descriptions follow a structured template
- dependency links are available and used consistently
- Seva permissions are explicit and limited
- webhook support exists or polling behavior is acceptable

Without those conditions, the integration will be functional at best, but not seamless.
