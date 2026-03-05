# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
from uuid import uuid4
from django.core.exceptions import ValidationError

from plane.db.models import (
    IssueHierarchyLink,
    Issue,
    Project,
    Workspace,
    State,
    User,
)


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create(
        email="testhierarchy@plane.so",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def workspace(db, user):
    """Create a test workspace"""
    return Workspace.objects.create(
        name="Test Workspace",
        slug="test-workspace-hierarchy",
        owner=user,
    )


@pytest.fixture
def project(db, workspace, user):
    """Create a test project"""
    return Project.objects.create(
        name="Test Project",
        identifier="TPH",
        workspace=workspace,
        created_by=user,
    )


@pytest.fixture
def state(db, project):
    """Create a test state"""
    return State.objects.create(
        name="Todo",
        project=project,
        group="backlog",
        default=True,
    )


@pytest.fixture
def issue_a(db, workspace, project, state, user):
    """Create issue A"""
    return Issue.objects.create(
        name="Issue A",
        workspace=workspace,
        project=project,
        state=state,
        created_by=user,
    )


@pytest.fixture
def issue_b(db, workspace, project, state, user):
    """Create issue B"""
    return Issue.objects.create(
        name="Issue B",
        workspace=workspace,
        project=project,
        state=state,
        created_by=user,
    )


@pytest.fixture
def issue_c(db, workspace, project, state, user):
    """Create issue C"""
    return Issue.objects.create(
        name="Issue C",
        workspace=workspace,
        project=project,
        state=state,
        created_by=user,
    )


@pytest.fixture
def different_project(db, workspace, user):
    """Create a different project in the same workspace"""
    return Project.objects.create(
        name="Different Project",
        identifier="DP",
        workspace=workspace,
        created_by=user,
    )


@pytest.fixture
def different_workspace(db, user):
    """Create a different workspace"""
    return Workspace.objects.create(
        name="Different Workspace",
        slug="different-workspace-hierarchy",
        owner=user,
    )


@pytest.mark.unit
class TestIssueHierarchyLinkModel:
    """Test the IssueHierarchyLink model"""

    @pytest.mark.django_db
    def test_create_hierarchy_link(self, workspace, project, state, user, issue_a, issue_b):
        """Test creating a valid hierarchy link"""
        link = IssueHierarchyLink.objects.create(
            parent_issue=issue_a,
            child_issue=issue_b,
            project=project,
            workspace=workspace,
            created_by=user,
            updated_by=user,
        )
        assert link.id is not None
        assert link.parent_issue_id == issue_a.id
        assert link.child_issue_id == issue_b.id

    @pytest.mark.django_db
    def test_cannot_link_to_self(self, workspace, project, state, user, issue_a):
        """Test that an issue cannot be linked to itself"""
        with pytest.raises(ValidationError) as exc_info:
            IssueHierarchyLink.objects.create(
                parent_issue=issue_a,
                child_issue=issue_a,
                project=project,
                workspace=workspace,
                created_by=user,
                updated_by=user,
            )
        assert "Cannot link an issue to itself" in str(exc_info.value)

    @pytest.mark.django_db
    def test_cannot_link_across_projects(self, workspace, project, state, user, issue_a, different_project):
        """Test that issues cannot be linked across different projects"""
        different_state = State.objects.create(
            name="Todo",
            project=different_project,
            group="backlog",
            default=True,
        )
        different_issue = Issue.objects.create(
            name="Different Issue",
            workspace=workspace,
            project=different_project,
            state=different_state,
            created_by=user,
        )

        with pytest.raises(ValidationError) as exc_info:
            IssueHierarchyLink.objects.create(
                parent_issue=issue_a,
                child_issue=different_issue,
                project=project,
                workspace=workspace,
                created_by=user,
                updated_by=user,
            )
        assert "same project" in str(exc_info.value)

    @pytest.mark.django_db
    def test_cannot_link_across_workspaces(self, workspace, different_workspace, project, state, user, issue_a):
        """Test that issues cannot be linked across different workspaces"""
        different_project = Project.objects.create(
            name="Different Project",
            identifier="DP",
            workspace=different_workspace,
            created_by=user,
        )
        different_state = State.objects.create(
            name="Todo",
            project=different_project,
            group="backlog",
            default=True,
        )
        different_issue = Issue.objects.create(
            name="Different Workspace Issue",
            workspace=different_workspace,
            project=different_project,
            state=different_state,
            created_by=user,
        )

        with pytest.raises(ValidationError) as exc_info:
            IssueHierarchyLink.objects.create(
                parent_issue=issue_a,
                child_issue=different_issue,
                project=project,
                workspace=workspace,
                created_by=user,
                updated_by=user,
            )
        assert "same workspace" in str(exc_info.value)

    @pytest.mark.django_db
    def test_unique_constraint(self, workspace, project, state, user, issue_a, issue_b):
        """Test that duplicate links cannot be created"""
        IssueHierarchyLink.objects.create(
            parent_issue=issue_a,
            child_issue=issue_b,
            project=project,
            workspace=workspace,
            created_by=user,
            updated_by=user,
        )

        with pytest.raises(Exception):
            IssueHierarchyLink.objects.create(
                parent_issue=issue_a,
                child_issue=issue_b,
                project=project,
                workspace=workspace,
                created_by=user,
                updated_by=user,
            )

    @pytest.mark.django_db
    def test_get_children(self, workspace, project, state, user, issue_a, issue_b, issue_c):
        """Test getting children of an issue"""
        IssueHierarchyLink.objects.create(
            parent_issue=issue_a,
            child_issue=issue_b,
            project=project,
            workspace=workspace,
            created_by=user,
            updated_by=user,
        )
        IssueHierarchyLink.objects.create(
            parent_issue=issue_a,
            child_issue=issue_c,
            project=project,
            workspace=workspace,
            created_by=user,
            updated_by=user,
        )

        children = issue_a.child_hierarchy_links.all()
        assert children.count() == 2

    @pytest.mark.django_db
    def test_get_parents(self, workspace, project, state, user, issue_a, issue_b, issue_c):
        """Test getting parents of an issue"""
        IssueHierarchyLink.objects.create(
            parent_issue=issue_a,
            child_issue=issue_c,
            project=project,
            workspace=workspace,
            created_by=user,
            updated_by=user,
        )
        IssueHierarchyLink.objects.create(
            parent_issue=issue_b,
            child_issue=issue_c,
            project=project,
            workspace=workspace,
            created_by=user,
            updated_by=user,
        )

        parents = issue_c.parent_hierarchy_links.all()
        assert parents.count() == 2


@pytest.mark.unit
class TestIssueHierarchyLinkCycleDetection:
    """Test cycle detection in hierarchy links"""

    @pytest.mark.django_db
    def test_no_cycle_simple(self, workspace, project, state, user, issue_a, issue_b):
        """Test that simple link doesn't create cycle"""
        link = IssueHierarchyLink.objects.create(
            parent_issue=issue_a,
            child_issue=issue_b,
            project=project,
            workspace=workspace,
            created_by=user,
            updated_by=user,
        )
        assert link.id is not None

    @pytest.mark.django_db
    def test_no_cycle_three_levels(self, workspace, project, state, user, issue_a, issue_b, issue_c):
        """Test that three-level hierarchy doesn't create cycle"""
        IssueHierarchyLink.objects.create(
            parent_issue=issue_a,
            child_issue=issue_b,
            project=project,
            workspace=workspace,
            created_by=user,
            updated_by=user,
        )
        IssueHierarchyLink.objects.create(
            parent_issue=issue_b,
            child_issue=issue_c,
            project=project,
            workspace=workspace,
            created_by=user,
            updated_by=user,
        )

        children = issue_a.child_hierarchy_links.all()
        assert children.count() == 1
        assert children.first().child_issue_id == issue_b.id

        grandchildren = issue_b.child_hierarchy_links.all()
        assert grandchildren.count() == 1
        assert grandchildren.first().child_issue_id == issue_c.id

    @pytest.mark.django_db
    def test_cannot_create_direct_cycle(self, workspace, project, state, user, issue_a, issue_b):
        """Test that direct cycle is prevented via validation"""
        IssueHierarchyLink.objects.create(
            parent_issue=issue_a,
            child_issue=issue_b,
            project=project,
            workspace=workspace,
            created_by=user,
            updated_by=user,
        )

        with pytest.raises(ValidationError) as exc_info:
            IssueHierarchyLink.objects.create(
                parent_issue=issue_b,
                child_issue=issue_a,
                project=project,
                workspace=workspace,
                created_by=user,
                updated_by=user,
            )
        assert "circular" in str(exc_info.value).lower() or "already an ancestor" in str(exc_info.value).lower()
