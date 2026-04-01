# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest

from plane.api.agent_config import ensure_seva_project_configuration, get_seva_issue_types
from plane.api.serializers import IssueSerializer
from plane.db.models import Issue, Project, ProjectMember, State


@pytest.mark.unit
class TestIssueApiSerializer:
    @pytest.mark.django_db
    def test_parent_work_item_cannot_move_to_done_with_open_child(self, workspace, create_user):
        project = Project.objects.create(
            name="Seva Project",
            identifier="SEVA",
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
        ensure_seva_project_configuration(project, create_user)

        states = {
            state.agent_state: state
            for state in State.all_state_objects.filter(project=project, deleted_at__isnull=True)
        }
        issue_types = {issue_type.name: issue_type for issue_type in get_seva_issue_types(project)}

        parent_issue = Issue.objects.create(
            name="Parent issue",
            project=project,
            state=states["in_progress"],
            type=issue_types["task"],
            created_by=create_user,
            updated_by=create_user,
        )
        Issue.objects.create(
            name="Open child issue",
            project=project,
            parent=parent_issue,
            state=states["ready"],
            type=issue_types["follow_up"],
            created_by=create_user,
            updated_by=create_user,
        )

        serializer = IssueSerializer(
            parent_issue,
            data={"state": str(states["done"].id)},
            context={"project_id": project.id, "workspace_id": project.workspace_id},
            partial=True,
        )

        assert not serializer.is_valid()
        assert serializer.errors == {"state": ["Parent work items cannot move to Done while child work remains open"]}
