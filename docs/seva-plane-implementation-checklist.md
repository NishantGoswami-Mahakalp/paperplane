# Seva + Plane Implementation Checklist

This checklist turns `docs/seva-plane-requirements.md` into a concrete implementation plan for the Paperplane agent.

Use this document when the goal is not just to document the integration, but to finish it end to end.

The concrete v1 decisions and runbook now live in `docs/seva-plane-setup.md`.

## Outcome

Seva can use Plane as its operational task system with:

- a dedicated and predictable project setup
- machine-readable workflow states and issue metadata
- explicit Seva permissions
- a working API or webhook integration path
- verified flows for claim, block, follow-up creation, and closure

## Implementation Order

Do the phases in order.

Do not start webhook or agent logic before the Plane-side workflow, labels, and permissions are standardized.

## Phase 1: Confirm Product Decisions

Goal: remove ambiguity before implementation starts.

Checklist:

- [ ] Decide which Plane workspace Seva will operate in
- [ ] Decide which Plane project or projects Seva may operate in
- [ ] Decide whether Seva gets a dedicated project or a shared project
- [ ] Decide whether Seva may auto-assign issues to itself
- [ ] Decide whether Seva may close only leaf issues or also close parents
- [ ] Decide whether labels or custom fields are the canonical source for severity and component
- [ ] Decide whether webhooks are required or whether polling is acceptable for v1

Definition of done:

- all seven decisions are written down in one source-controlled location
- no open ambiguity remains about Seva permissions or target projects

## Phase 2: Standardize Plane Workflow

Goal: make the issue workflow machine-readable and stable.

Checklist:

- [ ] Create or identify the exact workflow states Seva will use
- [ ] Ensure the following states exist: `backlog`, `ready`, `in_progress`, `blocked`, `in_review` or `needs_review`, `done`, `cancelled`
- [ ] Document the meaning of each state in operational terms
- [ ] Verify `ready` really means unblocked and actionable
- [ ] Verify `blocked` is used only for real blockers, not generic delay
- [ ] Verify `done` means acceptance criteria are satisfied

Verification:

- [ ] State list can be fetched through Plane API
- [ ] State names and IDs are stable across the target project

Definition of done:

- Seva can map every required execution state to a real Plane state without heuristics

## Phase 3: Standardize Issue Types And Labels

Goal: make work classification predictable.

Checklist:

- [ ] Create or confirm issue types: `bug`, `feature`, `task`, `ops`, `follow_up`
- [ ] Add optional types only if they are intentionally supported
- [ ] Create or confirm severity labels: `critical`, `high`, `medium`, `low`
- [ ] Create or confirm component labels: `api`, `web`, `auth`, `billing`, `infra`, `docs`
- [ ] Create or confirm environment labels if needed: `prod`, `staging`, `sandbox`
- [ ] Remove competing synonyms if they describe the same thing
- [ ] Document the allowed vocabulary

Verification:

- [ ] Labels can be listed through Plane API
- [ ] There is a one-to-one mapping between intended meanings and actual labels

Definition of done:

- Seva can infer issue type, severity, and component from stable Plane metadata

## Phase 4: Standardize Issue Templates

Goal: ensure issue descriptions contain enough structure for Seva to act safely.

Checklist:

- [ ] Create a canonical issue template for Seva-managed work
- [ ] Include sections for `Why`, `What`, `Acceptance Criteria`, `Dependencies`, and `Notes / Handoff`
- [ ] Decide where this template lives in Plane
- [ ] Ensure new Seva-facing issues are expected to follow the template
- [ ] Add at least one filled example for each major issue type

Verification:

- [ ] Human-created issues in the target project can follow the template without extra guidance
- [ ] Seva can parse required sections from sample issues

Definition of done:

- issue descriptions are consistently actionable without outside context

## Phase 5: Define Permissions And Identity

Goal: give Seva the access it needs without over-privileging it.

Checklist:

- [ ] Create a dedicated Seva service account or API token owner
- [ ] Scope Seva to allowed projects only if possible
- [ ] Grant read access to projects, states, labels, issues, comments, and members
- [ ] Grant write access to issue creation, issue updates, comments, and status transitions
- [ ] Confirm whether Seva may reassign issues
- [ ] Confirm whether Seva may close issues directly
- [ ] Confirm Seva does not have workspace-admin or user-management access
- [ ] Store credential setup steps securely and separately from public docs

Verification:

- [ ] Seva credentials can fetch project metadata
- [ ] Seva credentials can create and update a test issue
- [ ] Seva credentials cannot perform forbidden admin actions

Definition of done:

- Seva has the minimum viable permissions required for task execution and no more

## Phase 6: Confirm API Contract

Goal: validate that Plane API can support Seva without undocumented assumptions.

Checklist:

- [ ] Identify the endpoints Seva will use to list projects
- [ ] Identify the endpoints Seva will use to list states, labels, and members
- [ ] Identify the endpoints Seva will use to query actionable issues
- [ ] Identify the endpoints Seva will use to fetch issue details
- [ ] Identify the endpoints Seva will use to create issues
- [ ] Identify the endpoints Seva will use to update issue state, assignee, labels, and description
- [ ] Identify the endpoints Seva will use to add comments
- [ ] Identify the endpoints Seva will use to fetch links, blockers, sub-issues, or parent relationships
- [ ] Document authentication, pagination, and rate-limit behavior
- [ ] Document error shapes Seva must handle

Verification:

- [ ] Every required action has a tested API path
- [ ] There are no missing API capabilities for the required Seva flows

Definition of done:

- Paperplane agent has a complete API map for Seva integration work

## Phase 7: Implement Plane-Side Bootstrap Or Setup Script

Goal: make the setup repeatable.

Checklist:

- [ ] Decide whether setup is manual, scripted, or hybrid
- [ ] If scripted, create a bootstrap script or migration step that applies the required states, labels, and types
- [ ] If manual, create a runbook with exact setup steps and screenshots or IDs
- [ ] Ensure setup produces stable identifiers where Seva depends on them
- [ ] Record the target project IDs or slugs in a config file if needed

Verification:

- [ ] A fresh environment can be configured using the documented process
- [ ] A second operator can reproduce the same setup without tribal knowledge

Definition of done:

- Plane configuration for Seva is reproducible

## Phase 8: Implement Event Intake

Goal: let Seva react to Plane changes or poll them reliably.

Checklist for webhook approach:

- [ ] Enable webhook support for the target workspace or project
- [ ] Subscribe to issue created, updated, transitioned, assigned, commented, and completed events
- [ ] Validate request signing or another trust mechanism
- [ ] Implement retry-safe processing
- [ ] Ensure webhook payloads include enough identifiers to re-fetch full issue data

Checklist for polling approach:

- [ ] Define poll interval
- [ ] Define cursor or updated-since strategy
- [ ] Define deduplication behavior
- [ ] Define retry and backoff behavior

Definition of done:

- Seva has a reliable change-detection path and does not miss or duplicate issue transitions

## Phase 9: Implement Seva Workflow Behavior

Goal: make Seva operate predictably against Plane.

Checklist:

- [ ] Read `ready` issues only
- [ ] Claim work by moving issue to `in_progress`
- [ ] Add progress comments when meaningful changes occur
- [ ] Move issue to `blocked` when an external dependency prevents progress
- [ ] Create linked follow-up issues for newly discovered work
- [ ] Add blocker context in comments when blocking an issue
- [ ] Add completion notes before moving issue to `done`
- [ ] Enforce closure rules for parent-child relationships

Verification:

- [ ] Behavior is deterministic for the same issue input
- [ ] Comments and status changes are understandable to humans reading Plane later

Definition of done:

- Seva's issue behavior matches the rules in `docs/seva-plane-requirements.md`

## Phase 10: Build Acceptance Tests

Goal: prove the integration works in the real flows that matter.

Required tests:

- [ ] New work intake flow
- [ ] Discovered blocker flow
- [ ] Follow-up issue creation flow
- [ ] Successful completion flow
- [ ] Unauthorized or insufficient-permission failure flow
- [ ] Missing label or missing state configuration failure flow

Suggested test structure:

- fixture Plane project
- fixture issue states
- fixture labels and issue types
- test Seva credential
- expected comments and transitions

Definition of done:

- the acceptance-test set proves Seva can operate without manual intervention in the supported flows

## Phase 11: Operational Readiness

Goal: make the integration supportable by humans.

Checklist:

- [ ] Document setup in docs
- [ ] Document credential rotation process
- [ ] Document failure modes and retry behavior
- [ ] Document which projects Seva is allowed to act in
- [ ] Document escalation path for blocked or unsafe actions
- [ ] Document how to disable Seva access quickly if needed

Definition of done:

- another engineer can operate and troubleshoot the integration without reverse-engineering it

## Definition Of Complete

The Seva x Plane implementation is complete only when all of the following are true:

- [ ] target Plane project setup is standardized
- [ ] required states, labels, and issue types exist
- [ ] issue templates are defined and usable
- [ ] Seva credentials and permissions are configured
- [ ] API endpoints used by Seva are documented and tested
- [ ] webhook or polling ingestion is implemented
- [ ] Seva can claim, block, create follow-ups, and close issues
- [ ] acceptance tests pass for the supported flows
- [ ] operational documentation exists

## Current Gaps To Close

Based on the current Paperplane review, these items are still missing and should be treated as the first implementation targets:

- [ ] create Seva-specific Plane project or approved-project configuration
- [ ] standardize required Seva workflow states
- [ ] standardize issue types and label taxonomy
- [ ] define and document Seva issue template
- [ ] create Seva service account and permission model
- [ ] implement webhook consumer or polling adapter
- [ ] prove end-to-end Seva flows with acceptance tests

## Recommended First Three Tasks

If implementation begins immediately, start here:

1. Standardize the Plane project setup for Seva.
2. Create the Seva credential and API contract map.
3. Implement and test the `ready -> in_progress -> blocked/follow_up -> done` workflow path.
