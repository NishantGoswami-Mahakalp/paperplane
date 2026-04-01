import json
from io import StringIO

import pytest
from django.core.management import call_command

from plane.db.models import IssueTemplate, IssueType, Label, Project, ProjectIssueType, ProjectMember, State


@pytest.fixture
def project(db, workspace, create_user):
    project = Project.objects.create(
        name="Bootstrap Project",
        identifier="BOOT",
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


@pytest.mark.unit
@pytest.mark.django_db
def test_bootstrap_seva_project_command_is_idempotent(workspace, project):
    first_stdout = StringIO()
    second_stdout = StringIO()

    call_command(
        "bootstrap_seva_project",
        workspace=workspace.slug,
        project_id=str(project.id),
        stdout=first_stdout,
    )
    call_command(
        "bootstrap_seva_project",
        workspace=workspace.slug,
        project_id=str(project.id),
        stdout=second_stdout,
    )

    first_payload = json.loads(first_stdout.getvalue())
    second_payload = json.loads(second_stdout.getvalue())

    assert first_payload["configuration"]["is_ready"] is True
    assert second_payload["configuration"]["is_ready"] is True
    assert State.all_state_objects.filter(project=project, deleted_at__isnull=True).count() == 7
    assert (
        IssueType.objects.filter(
            workspace=project.workspace, name__in=["task", "bug", "feature", "ops", "follow_up"]
        ).count()
        == 5
    )
    assert ProjectIssueType.objects.filter(project=project, deleted_at__isnull=True).count() == 5
    assert Label.objects.filter(project=project, deleted_at__isnull=True).count() == 16
    assert IssueTemplate.objects.filter(project=project, name="Seva Work Item").count() == 1
