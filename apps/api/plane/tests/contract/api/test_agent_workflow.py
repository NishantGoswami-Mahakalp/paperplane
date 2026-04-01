from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from plane.api.agent_config import ensure_seva_project_configuration, get_seva_issue_types
from plane.db.models import APIToken, Issue, IssueRelation, Label, Project, ProjectMember, State
from plane.db.models.issue import IssueRelationChoices


@pytest.fixture
def project(db, workspace, create_user):
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
    return project


def _state_map(project):
    return {
        state.agent_state: state for state in State.all_state_objects.filter(project=project, deleted_at__isnull=True)
    }


def _issue_type_map(project):
    return {issue_type.name: issue_type for issue_type in get_seva_issue_types(project)}


@pytest.mark.contract
class TestSevaAgentWorkflow:
    def project_agent_context_url(self, workspace_slug, project_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/agent-context/"

    def ready_work_items_url(self, workspace_slug, project_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/agent-ready-work-items/"

    def updates_url(self, workspace_slug, project_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/agent-updates/"

    def comment_updates_url(self, workspace_slug, project_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/agent-comment-updates/"

    def work_item_url(self, workspace_slug, project_id, issue_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{issue_id}/"

    def work_item_context_url(self, workspace_slug, project_id, issue_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{issue_id}/agent-context/"

    def work_item_comment_url(self, workspace_slug, project_id, issue_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{issue_id}/comments/"

    def work_item_relation_url(self, workspace_slug, project_id, issue_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{issue_id}/relations/"

    @pytest.mark.django_db
    def test_agent_context_reports_missing_seva_configuration(self, api_key_client, workspace, project):
        response = api_key_client.get(self.project_agent_context_url(workspace.slug, project.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["seva_configuration"]["is_ready"] is False
        assert "ready" in response.data["seva_configuration"]["missing"]["states"]
        assert "task" in response.data["seva_configuration"]["missing"]["issue_types"]
        assert response.data["seva_configuration"]["missing"]["labels"]["severity"] == [
            "critical",
            "high",
            "medium",
            "low",
        ]
        assert response.data["seva_configuration"]["missing"]["issue_template"] is True

    @pytest.mark.django_db
    def test_agent_context_returns_bootstrapped_seva_configuration(
        self, api_key_client, workspace, project, create_user
    ):
        ensure_seva_project_configuration(project, create_user)

        response = api_key_client.get(self.project_agent_context_url(workspace.slug, project.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["seva_configuration"]["is_ready"] is True
        assert response.data["description_template"]["sections"] == [
            "Why",
            "What",
            "Acceptance Criteria",
            "Dependencies",
            "Notes / Handoff",
        ]
        assert {issue_type["name"] for issue_type in response.data["issue_types"]} == {
            "task",
            "bug",
            "feature",
            "ops",
            "follow_up",
        }
        assert sorted(
            label["name"] for label in response.data["seva_configuration"]["label_taxonomy"]["component"]
        ) == [
            "api",
            "auth",
            "billing",
            "docs",
            "infra",
            "web",
        ]

    @pytest.mark.django_db
    def test_agent_context_requires_taxonomy_labels_under_correct_roots(
        self, api_key_client, workspace, project, create_user
    ):
        ensure_seva_project_configuration(project, create_user)
        severity_root = Label.objects.get(project=project, name="severity")
        wrong_root = Label.objects.get(project=project, name="component")
        misplaced_label = Label.objects.get(project=project, name="critical")
        misplaced_label.parent = wrong_root
        misplaced_label.updated_by = create_user
        misplaced_label.save(update_fields=["parent", "updated_by"])

        response = api_key_client.get(self.project_agent_context_url(workspace.slug, project.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["seva_configuration"]["is_ready"] is False
        assert response.data["seva_configuration"]["missing"]["labels"]["severity"] == ["critical"]
        assert all(
            label["name"] != "critical"
            for label in response.data["seva_configuration"]["label_taxonomy"][severity_root.name]
        )

    @pytest.mark.django_db
    def test_agent_updates_cursor_tracks_changed_work_items(self, api_key_client, workspace, project, create_user):
        ensure_seva_project_configuration(project, create_user)
        states = _state_map(project)
        issue_types = _issue_type_map(project)

        first_issue = Issue.objects.create(
            name="First ready issue",
            project=project,
            state=states["ready"],
            type=issue_types["task"],
            created_by=create_user,
            updated_by=create_user,
        )
        second_issue = Issue.objects.create(
            name="Second ready issue",
            project=project,
            state=states["ready"],
            type=issue_types["task"],
            created_by=create_user,
            updated_by=create_user,
        )

        first_response = api_key_client.get(f"{self.updates_url(workspace.slug, project.id)}?limit=1")
        assert first_response.status_code == status.HTTP_200_OK
        assert len(first_response.data["results"]) == 1
        assert first_response.data["results"][0]["id"] == first_issue.id

        next_cursor = first_response.data["polling"]["next_cursor"]
        second_response = api_key_client.get(
            f"{self.updates_url(workspace.slug, project.id)}?cursor={next_cursor}&limit=10"
        )

        assert second_response.status_code == status.HTTP_200_OK
        assert [result["id"] for result in second_response.data["results"]] == [second_issue.id]

    @pytest.mark.django_db
    def test_agent_comment_updates_cursor_tracks_changed_comments(
        self, api_key_client, workspace, project, create_user
    ):
        ensure_seva_project_configuration(project, create_user)
        states = _state_map(project)
        issue_types = _issue_type_map(project)

        issue = Issue.objects.create(
            name="Commented issue",
            project=project,
            state=states["ready"],
            type=issue_types["task"],
            created_by=create_user,
            updated_by=create_user,
        )

        first_comment = api_key_client.post(
            self.work_item_comment_url(workspace.slug, project.id, issue.id),
            {"comment_html": "<p>First comment.</p>"},
            format="json",
        )
        assert first_comment.status_code == status.HTTP_201_CREATED

        first_response = api_key_client.get(f"{self.comment_updates_url(workspace.slug, project.id)}?limit=1")
        assert first_response.status_code == status.HTTP_200_OK
        assert len(first_response.data["results"]) == 1
        assert first_response.data["results"][0]["issue_id"] == issue.id

        second_comment = api_key_client.post(
            self.work_item_comment_url(workspace.slug, project.id, issue.id),
            {"comment_html": "<p>Second comment.</p>"},
            format="json",
        )
        assert second_comment.status_code == status.HTTP_201_CREATED

        next_cursor = first_response.data["polling"]["next_cursor"]
        second_response = api_key_client.get(
            f"{self.comment_updates_url(workspace.slug, project.id)}?cursor={next_cursor}"
        )
        assert second_response.status_code == status.HTTP_200_OK
        assert len(second_response.data["results"]) == 1
        assert second_response.data["results"][0]["comment_html"] == "<p>Second comment.</p>"

    @pytest.mark.django_db
    def test_work_item_relations_endpoint_creates_blocked_by_links(
        self,
        api_key_client,
        workspace,
        project,
        create_user,
    ):
        ensure_seva_project_configuration(project, create_user)
        states = _state_map(project)
        issue_types = _issue_type_map(project)

        origin_issue = Issue.objects.create(
            name="Origin issue",
            project=project,
            state=states["ready"],
            type=issue_types["task"],
            created_by=create_user,
            updated_by=create_user,
        )
        blocker_issue = Issue.objects.create(
            name="Blocker issue",
            project=project,
            state=states["ready"],
            type=issue_types["follow_up"],
            created_by=create_user,
            updated_by=create_user,
        )

        response = api_key_client.post(
            self.work_item_relation_url(workspace.slug, project.id, origin_issue.id),
            {"relation_type": "blocked_by", "issues": [str(blocker_issue.id)]},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["relations"]["blocked_by"][0]["id"] == blocker_issue.id
        assert IssueRelation.objects.filter(
            issue=origin_issue,
            related_issue=blocker_issue,
            relation_type=IssueRelationChoices.BLOCKED_BY.value,
        ).exists()

    @pytest.mark.django_db
    def test_ready_to_in_progress_blocked_follow_up_done_flow(
        self,
        api_key_client,
        workspace,
        project,
        create_user,
    ):
        ensure_seva_project_configuration(project, create_user)
        states = _state_map(project)
        issue_types = _issue_type_map(project)

        origin_issue = Issue.objects.create(
            name="Implement Seva Plane sync",
            project=project,
            state=states["ready"],
            type=issue_types["task"],
            description_html="<h2>Why</h2><p>Need a real integration.</p>",
            priority="high",
            created_by=create_user,
            updated_by=create_user,
        )

        ready_response = api_key_client.get(self.ready_work_items_url(workspace.slug, project.id))
        assert ready_response.status_code == status.HTTP_200_OK
        assert ready_response.data["results"][0]["id"] == origin_issue.id

        claim_response = api_key_client.patch(
            self.work_item_url(workspace.slug, project.id, origin_issue.id),
            {"state": str(states["in_progress"].id)},
            format="json",
        )
        assert claim_response.status_code == status.HTTP_200_OK
        origin_issue.refresh_from_db()
        assert origin_issue.state_id == states["in_progress"].id

        progress_comment = api_key_client.post(
            self.work_item_comment_url(workspace.slug, project.id, origin_issue.id),
            {"comment_html": "<p>Started implementation.</p>"},
            format="json",
        )
        assert progress_comment.status_code == status.HTTP_201_CREATED

        follow_up_response = api_key_client.post(
            f"/api/v1/workspaces/{workspace.slug}/projects/{project.id}/work-items/",
            {
                "name": "Provision missing Plane metadata",
                "description_html": "<h2>Why</h2><p>Need standardized setup.</p>",
                "state": str(states["ready"].id),
                "parent": str(origin_issue.id),
                "type_id": str(issue_types["follow_up"].id),
                "priority": "high",
            },
            format="json",
        )
        assert follow_up_response.status_code == status.HTTP_201_CREATED
        follow_up_issue = Issue.objects.get(pk=follow_up_response.data["id"])

        block_link_response = api_key_client.post(
            self.work_item_relation_url(workspace.slug, project.id, origin_issue.id),
            {"relation_type": "blocked_by", "issues": [str(follow_up_issue.id)]},
            format="json",
        )
        assert block_link_response.status_code == status.HTTP_201_CREATED

        block_response = api_key_client.patch(
            self.work_item_url(workspace.slug, project.id, origin_issue.id),
            {"state": str(states["blocked"].id)},
            format="json",
        )
        assert block_response.status_code == status.HTTP_200_OK

        blocked_comment = api_key_client.post(
            self.work_item_comment_url(workspace.slug, project.id, origin_issue.id),
            {"comment_html": "<p>Blocked on the linked follow-up issue.</p>"},
            format="json",
        )
        assert blocked_comment.status_code == status.HTTP_201_CREATED

        blocked_context = api_key_client.get(self.work_item_context_url(workspace.slug, project.id, origin_issue.id))
        assert blocked_context.status_code == status.HTTP_200_OK
        assert blocked_context.data["work_item"]["state"]["agent_state"] == "blocked"
        assert blocked_context.data["work_item"]["open_blockers"][0]["id"] == follow_up_issue.id
        assert blocked_context.data["work_item"]["hierarchy"]["children"][0]["id"] == follow_up_issue.id

        follow_up_done = api_key_client.patch(
            self.work_item_url(workspace.slug, project.id, follow_up_issue.id),
            {"state": str(states["done"].id)},
            format="json",
        )
        assert follow_up_done.status_code == status.HTTP_200_OK

        follow_up_note = api_key_client.post(
            self.work_item_comment_url(workspace.slug, project.id, follow_up_issue.id),
            {"comment_html": "<p>Follow-up work completed.</p>"},
            format="json",
        )
        assert follow_up_note.status_code == status.HTTP_201_CREATED

        complete_response = api_key_client.patch(
            self.work_item_url(workspace.slug, project.id, origin_issue.id),
            {"state": str(states["done"].id)},
            format="json",
        )
        assert complete_response.status_code == status.HTTP_200_OK

        completion_note = api_key_client.post(
            self.work_item_comment_url(workspace.slug, project.id, origin_issue.id),
            {"comment_html": "<p>Acceptance criteria met and integration is complete.</p>"},
            format="json",
        )
        assert completion_note.status_code == status.HTTP_201_CREATED

        final_context = api_key_client.get(self.work_item_context_url(workspace.slug, project.id, origin_issue.id))
        assert final_context.status_code == status.HTTP_200_OK
        assert final_context.data["work_item"]["state"]["agent_state"] == "done"
        assert final_context.data["work_item"]["open_blockers"] == []

    @pytest.mark.django_db
    def test_comment_creation_succeeds_when_async_dispatch_fails(
        self,
        api_key_client,
        workspace,
        project,
        create_user,
    ):
        ensure_seva_project_configuration(project, create_user)
        states = _state_map(project)
        issue_types = _issue_type_map(project)

        issue = Issue.objects.create(
            name="Comment resilience issue",
            project=project,
            state=states["ready"],
            type=issue_types["task"],
            created_by=create_user,
            updated_by=create_user,
        )

        with patch("plane.api.views.issue.issue_activity.delay", side_effect=RuntimeError("broker unavailable")):
            with patch("plane.api.views.issue.model_activity.delay", side_effect=RuntimeError("broker unavailable")):
                response = api_key_client.post(
                    self.work_item_comment_url(workspace.slug, project.id, issue.id),
                    {"comment_html": "<p>Still persists without broker.</p>"},
                    format="json",
                )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["comment_html"] == "<p>Still persists without broker.</p>"

    @pytest.mark.django_db
    def test_work_item_transition_succeeds_when_activity_dispatch_fails(
        self,
        api_key_client,
        workspace,
        project,
        create_user,
    ):
        ensure_seva_project_configuration(project, create_user)
        states = _state_map(project)
        issue_types = _issue_type_map(project)

        issue = Issue.objects.create(
            name="Transition resilience issue",
            project=project,
            state=states["ready"],
            type=issue_types["task"],
            created_by=create_user,
            updated_by=create_user,
        )

        with patch("plane.api.views.issue.issue_activity.delay", side_effect=RuntimeError("broker unavailable")):
            response = api_key_client.patch(
                self.work_item_url(workspace.slug, project.id, issue.id),
                {"state": str(states["in_progress"].id)},
                format="json",
            )

        assert response.status_code == status.HTTP_200_OK
        issue.refresh_from_db()
        assert issue.state_id == states["in_progress"].id

    @pytest.mark.django_db
    def test_parent_issue_cannot_move_to_done_while_child_is_open(
        self,
        api_key_client,
        workspace,
        project,
        create_user,
    ):
        ensure_seva_project_configuration(project, create_user)
        states = _state_map(project)
        issue_types = _issue_type_map(project)

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

        response = api_key_client.patch(
            self.work_item_url(workspace.slug, project.id, parent_issue.id),
            {"state": str(states["done"].id)},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["state"] == ["Parent work items cannot move to Done while child work remains open"]

    @pytest.mark.django_db
    def test_relation_endpoint_requires_authentication(self, api_client, workspace, project, create_user):
        ensure_seva_project_configuration(project, create_user)
        states = _state_map(project)
        issue_types = _issue_type_map(project)
        origin_issue = Issue.objects.create(
            name="Origin issue",
            project=project,
            state=states["ready"],
            type=issue_types["task"],
            created_by=create_user,
            updated_by=create_user,
        )
        blocker_issue = Issue.objects.create(
            name="Blocker issue",
            project=project,
            state=states["ready"],
            type=issue_types["follow_up"],
            created_by=create_user,
            updated_by=create_user,
        )

        response = api_client.post(
            self.work_item_relation_url(workspace.slug, project.id, origin_issue.id),
            {"relation_type": "blocked_by", "issues": [str(blocker_issue.id)]},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_service_token_is_scoped_to_allowed_project_ids(self, workspace, create_user):
        allowed_project = Project.objects.create(
            name="Allowed Seva Project",
            identifier="ALWD",
            workspace=workspace,
            created_by=create_user,
            updated_by=create_user,
        )
        blocked_project = Project.objects.create(
            name="Blocked Seva Project",
            identifier="BLKD",
            workspace=workspace,
            created_by=create_user,
            updated_by=create_user,
        )
        for project in [allowed_project, blocked_project]:
            ProjectMember.objects.create(
                project=project,
                member=create_user,
                role=20,
                is_active=True,
                created_by=create_user,
                updated_by=create_user,
            )
            ensure_seva_project_configuration(project, create_user)

        token = APIToken.objects.create(
            label="Scoped Seva Token",
            user=create_user,
            user_type=0,
            workspace=workspace,
            is_service=True,
            allowed_project_ids=[str(allowed_project.id)],
        )
        client = APIClient()
        client.credentials(HTTP_X_API_KEY=token.token)

        allowed_response = client.get(self.project_agent_context_url(workspace.slug, allowed_project.id))
        blocked_response = client.get(self.project_agent_context_url(workspace.slug, blocked_project.id))

        assert allowed_response.status_code == status.HTTP_200_OK
        assert blocked_response.status_code == status.HTTP_403_FORBIDDEN
