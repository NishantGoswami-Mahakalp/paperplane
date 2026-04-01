# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
from rest_framework import status

from plane.db.models import Issue, IssueHierarchyLink, IssueRelation, Label, Project, ProjectMember, State
from plane.db.models.issue import IssueRelationChoices


@pytest.fixture
def project(db, workspace, create_user):
    project = Project.objects.create(
        name="Test Project",
        identifier="TP",
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
    return project


@pytest.fixture
def ready_state(project, create_user):
    return State.objects.create(
        name="Ready",
        color="#60646C",
        group="unstarted",
        agent_state="ready",
        project=project,
        workspace=project.workspace,
        created_by=create_user,
        updated_by=create_user,
    )


@pytest.fixture
def in_progress_state(project, create_user):
    return State.objects.create(
        name="In Progress",
        color="#F59E0B",
        group="started",
        agent_state="in_progress",
        project=project,
        workspace=project.workspace,
        created_by=create_user,
        updated_by=create_user,
    )


@pytest.fixture
def done_state(project, create_user):
    return State.objects.create(
        name="Done",
        color="#46A758",
        group="completed",
        agent_state="done",
        project=project,
        workspace=project.workspace,
        created_by=create_user,
        updated_by=create_user,
    )


@pytest.mark.contract
class TestAgentAPIEndpoints:
    def get_project_agent_context_url(self, workspace_slug, project_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/agent-context/"

    def get_ready_work_items_url(self, workspace_slug, project_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/agent-ready-work-items/"

    def get_work_item_agent_context_url(self, workspace_slug, project_id, issue_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{issue_id}/agent-context/"

    @pytest.mark.django_db
    def test_project_agent_context_returns_normalized_capabilities(
        self,
        api_key_client,
        workspace,
        project,
        ready_state,
        create_user,
    ):
        Label.objects.create(
            name="api",
            color="#0000FF",
            project=project,
            workspace=workspace,
            created_by=create_user,
            updated_by=create_user,
        )

        response = api_key_client.get(self.get_project_agent_context_url(workspace.slug, project.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["project"]["id"] == project.id
        assert response.data["description_template"]["sections"] == [
            "Why",
            "What",
            "Acceptance Criteria",
            "Dependencies",
            "Notes / Handoff",
        ]
        assert response.data["states"][0]["agent_state"] == ready_state.agent_state
        assert response.data["labels"][0]["name"] == "api"
        assert response.data["members"][0]["email"] == create_user.email

    @pytest.mark.django_db
    def test_ready_work_items_only_returns_actionable_ready_items(
        self,
        api_key_client,
        workspace,
        project,
        ready_state,
        in_progress_state,
        create_user,
    ):
        ready_issue = Issue.objects.create(
            name="Actionable issue",
            project=project,
            state=ready_state,
            created_by=create_user,
            updated_by=create_user,
        )
        blocked_issue = Issue.objects.create(
            name="Blocked ready issue",
            project=project,
            state=ready_state,
            created_by=create_user,
            updated_by=create_user,
        )
        blocking_issue = Issue.objects.create(
            name="Blocking issue",
            project=project,
            state=in_progress_state,
            created_by=create_user,
            updated_by=create_user,
        )
        IssueRelation.objects.create(
            issue=blocked_issue,
            related_issue=blocking_issue,
            relation_type=IssueRelationChoices.BLOCKED_BY.value,
            project=project,
            workspace=workspace,
            created_by=create_user,
            updated_by=create_user,
        )

        response = api_key_client.get(self.get_ready_work_items_url(workspace.slug, project.id))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == ready_issue.id

        all_ready_response = api_key_client.get(
            f"{self.get_ready_work_items_url(workspace.slug, project.id)}?actionable=false"
        )

        assert all_ready_response.status_code == status.HTTP_200_OK
        assert len(all_ready_response.data["results"]) == 2

        blocked_payload = next(
            result for result in all_ready_response.data["results"] if result["id"] == blocked_issue.id
        )
        assert blocked_payload["is_actionable"] is False
        assert blocked_payload["open_blockers"][0]["id"] == blocking_issue.id

    @pytest.mark.django_db
    def test_work_item_agent_context_includes_relations_and_hierarchy(
        self,
        api_key_client,
        workspace,
        project,
        ready_state,
        done_state,
        create_user,
    ):
        parent_issue = Issue.objects.create(
            name="Parent issue",
            project=project,
            state=ready_state,
            created_by=create_user,
            updated_by=create_user,
        )
        child_issue = Issue.objects.create(
            name="Child issue",
            project=project,
            state=ready_state,
            created_by=create_user,
            updated_by=create_user,
        )
        resolved_blocker = Issue.objects.create(
            name="Resolved blocker",
            project=project,
            state=done_state,
            created_by=create_user,
            updated_by=create_user,
        )
        IssueHierarchyLink.objects.create(
            parent_issue=parent_issue,
            child_issue=child_issue,
            project=project,
            workspace=workspace,
            created_by=create_user,
            updated_by=create_user,
        )
        IssueRelation.objects.create(
            issue=child_issue,
            related_issue=resolved_blocker,
            relation_type=IssueRelationChoices.BLOCKED_BY.value,
            project=project,
            workspace=workspace,
            created_by=create_user,
            updated_by=create_user,
        )

        response = api_key_client.get(self.get_work_item_agent_context_url(workspace.slug, project.id, child_issue.id))

        assert response.status_code == status.HTTP_200_OK
        work_item = response.data["work_item"]
        assert work_item["hierarchy"]["parents"][0]["id"] == parent_issue.id
        assert work_item["relations"]["blocked_by"][0]["id"] == resolved_blocker.id
        assert work_item["open_blockers"] == []
        assert work_item["is_actionable"] is True
