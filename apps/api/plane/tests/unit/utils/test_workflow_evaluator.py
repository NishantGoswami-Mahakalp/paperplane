# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
from unittest.mock import MagicMock, patch

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
        mock_issue.project_id = "project-1"
        mock_issue.type = None

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
        mock_issue.project_id = "project-1"
        mock_issue.type = None

        mock_old_state = MagicMock()
        mock_old_state.id = "state-1"
        mock_old_state.name = "Old State"

        mock_new_state = MagicMock()
        mock_new_state.id = "state-2"
        mock_new_state.name = "New State"

        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = False
        mock_transitions.filter.return_value = mock_queryset

        evaluator = WorkflowEvaluator(mock_issue)
        result = evaluator.validate_transition(mock_old_state, mock_new_state)

        assert result is True

    @patch("plane.utils.workflow_evaluator.WorkflowTransition.objects")
    def test_validate_transition_no_old_state(self, mock_transitions):
        """Test validation passes when old state is None"""
        mock_issue = MagicMock()
        mock_issue.project_id = "project-1"
        mock_issue.type = None

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
        evaluator = WorkflowEvaluator(mock_issue)

        result = evaluator._evaluate_conditions({})
        assert result is True

        result = evaluator._evaluate_conditions(None)
        assert result is True

    def test_evaluate_conditions_with_data(self):
        """Test condition evaluation with conditions"""
        mock_issue = MagicMock()
        evaluator = WorkflowEvaluator(mock_issue)

        result = evaluator._evaluate_conditions({"some": "condition"})
        assert result is True
