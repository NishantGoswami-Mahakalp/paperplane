# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from typing import TYPE_CHECKING, Optional

from django.db import models

from plane.db.models import Issue, State, WorkflowTransition

if TYPE_CHECKING:
    from plane.db.models import WorkflowState


class WorkflowTransitionError(Exception):
    def __init__(self, message: str, code: str = "INVALID_TRANSITION"):
        self.message = message
        self.code = code
        super().__init__(message)


class WorkflowEvaluator:
    def __init__(self, issue: "Issue"):
        self.issue = issue
        self.project = issue.project
        self.issue_type = issue.type

    def validate_transition(
        self,
        old_state: Optional["State"],
        new_state: "State",
    ) -> bool:
        if old_state is None or old_state.id == new_state.id:
            return True

        project = self.project
        issue_type = self.issue_type

        transitions = WorkflowTransition.objects.filter(
            project=project,
            from_state__isnull=False,
            to_state__isnull=False,
        )

        if issue_type:
            transitions = transitions.filter(models.Q(item_type=issue_type) | models.Q(item_type__isnull=True))
        else:
            transitions = transitions.filter(item_type__isnull=True)

        if not transitions.exists():
            return True

        valid_transition = False
        for transition in transitions:
            if self._is_valid_transition(transition, old_state, new_state):
                valid_transition = True
                if not self._evaluate_conditions(transition.condition_json):
                    raise WorkflowTransitionError(
                        message=f"Transition conditions not met for '{transition.name}'",
                        code="TRANSITION_CONDITIONS_NOT_MET",
                    )
                return True

        if not valid_transition:
            raise WorkflowTransitionError(
                message=f"No valid transition from '{old_state.name}' to '{new_state.name}'",
                code="INVALID_WORKFLOW_TRANSITION",
            )

        return True

    def _is_valid_transition(
        self,
        transition: WorkflowTransition,
        old_state: "State",
        new_state: "State",
    ) -> bool:
        from_state = transition.from_state
        to_state = transition.to_state

        if hasattr(from_state, "state") and hasattr(to_state, "state"):
            old_state_id = getattr(old_state, "state_id", None) or old_state.id
            new_state_id = getattr(new_state, "state_id", None) or new_state.id
            return from_state.state_id == old_state_id and to_state.state_id == new_state_id

        return False

    def _evaluate_conditions(self, condition_json: dict) -> bool:
        if not condition_json:
            return True

        return True
