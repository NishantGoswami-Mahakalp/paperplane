# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
from unittest.mock import MagicMock, patch

from plane.db.models import Issue, IssueType, Project, ProjectIssueType, ProjectMember, State
from plane.utils.workflow_evaluator import WorkflowEvaluator, WorkflowTransitionError


@pytest.mark.unit
class TestWorkflowEvaluator:
    """Test the WorkflowEvaluator service"""

    def test_workflow_transition_error_init(self):
        """Test WorkflowTransitionError initialization"""
        error = WorkflowTransitionError("Test error message", "TEST_CODE")
        assert error.message == "Test error message"
        assert error.code == "TEST_CODE"
        assert str(error) == "Test error message"

    def test_workflow_transition_error_default_code(self):
        """Test WorkflowTransitionError default code"""
        error = WorkflowTransitionError("Test error message")
        assert error.code == "INVALID_TRANSITION"

    @patch("plane.utils.workflow_evaluator.WorkflowTransition.objects")
    def test_validate_transition_same_state(self, mock_transitions):
        """Test validation passes when old and new state are the same"""
        mock_issue = MagicMock()
        mock_issue.project = None
        mock_issue.project_id = "project-1"
        mock_issue.type = None
        mock_issue.type_id = None

        mock_old_state = MagicMock()
        mock_old_state.id = "state-1"
        mock_old_state.name = "Test State"

        mock_new_state = MagicMock()
        mock_new_state.id = "state-1"
        mock_new_state.name = "Test State"

        evaluator = WorkflowEvaluator(mock_issue)
        result = evaluator.validate_transition(mock_old_state, mock_new_state)

        assert result is True
        mock_transitions.filter.assert_not_called()

    @patch("plane.utils.workflow_evaluator.WorkflowTransition.objects")
    def test_validate_transition_no_transitions_defined(self, mock_transitions):
        """Test validation passes when no transitions are defined (backward compatible)"""
        mock_issue = MagicMock()
        mock_issue.project = None
        mock_issue.project_id = "project-1"
        mock_issue.type = None
        mock_issue.type_id = None

        mock_old_state = MagicMock()
        mock_old_state.id = "state-1"
        mock_old_state.name = "Old State"

        mock_new_state = MagicMock()
        mock_new_state.id = "state-2"
        mock_new_state.name = "New State"

        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.exists.return_value = False
        mock_transitions.filter.return_value = mock_queryset

        evaluator = WorkflowEvaluator(mock_issue)
        result = evaluator.validate_transition(mock_old_state, mock_new_state)

        assert result is True

    @patch("plane.utils.workflow_evaluator.WorkflowTransition.objects")
    def test_validate_transition_no_old_state(self, mock_transitions):
        """Test validation passes when old state is None"""
        mock_issue = MagicMock()
        mock_issue.project = None
        mock_issue.project_id = "project-1"
        mock_issue.type = None
        mock_issue.type_id = None

        mock_new_state = MagicMock()
        mock_new_state.id = "state-2"
        mock_new_state.name = "New State"

        evaluator = WorkflowEvaluator(mock_issue)
        result = evaluator.validate_transition(None, mock_new_state)

        assert result is True
        mock_transitions.filter.assert_not_called()

    def test_evaluate_conditions_empty(self):
        """Test condition evaluation with empty conditions"""
        mock_issue = MagicMock()
        mock_issue.project = None
        mock_issue.type = None
        mock_issue.type_id = None
        evaluator = WorkflowEvaluator(mock_issue)

        result = evaluator._evaluate_conditions({})
        assert result is True

        result = evaluator._evaluate_conditions(None)
        assert result is True

    def test_evaluate_conditions_with_data(self):
        """Test condition evaluation with conditions"""
        mock_issue = MagicMock()
        mock_issue.project = None
        mock_issue.type = None
        mock_issue.type_id = None
        evaluator = WorkflowEvaluator(mock_issue)

        result = evaluator._evaluate_conditions({"some": "condition"})
        assert result is True

    @pytest.mark.django_db
    def test_validate_transition_uses_project_issue_type(self, workspace, create_user):
        project = Project.objects.create(
            name="Workflow Project",
            identifier="WF",
            workspace=workspace,
            created_by=create_user,
            updated_by=create_user,
        )
        ProjectMember.objects.create(
            project=project,
            member=create_user,
            role=20,
            is_active=True,
            created_by=create_user,
            updated_by=create_user,
        )
        issue_type = IssueType.objects.create(
            workspace=workspace,
            name="task",
            is_active=True,
            created_by=create_user,
            updated_by=create_user,
        )
        ProjectIssueType.objects.create(
            project=project,
            workspace=workspace,
            issue_type=issue_type,
            created_by=create_user,
            updated_by=create_user,
        )
        old_state = State.objects.create(
            name="Ready",
            color="#3E63DD",
            group="unstarted",
            project=project,
            workspace=workspace,
            created_by=create_user,
            updated_by=create_user,
        )
        new_state = State.objects.create(
            name="In Progress",
            color="#F59E0B",
            group="started",
            project=project,
            workspace=workspace,
            created_by=create_user,
            updated_by=create_user,
        )
        issue = Issue.objects.create(
            name="Typed issue",
            project=project,
            state=old_state,
            type=issue_type,
            created_by=create_user,
            updated_by=create_user,
        )

        assert WorkflowEvaluator(issue).validate_transition(old_state, new_state) is True
