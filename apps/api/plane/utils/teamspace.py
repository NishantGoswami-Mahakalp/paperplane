# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.db.models import Q
from plane.db.models import TeamspaceMember, TeamspaceProject


def get_teamspace_member_ids(user, workspace_slug):
    """Get all teamspace IDs the user is a member of."""
    return list(
        TeamspaceMember.objects.filter(
            member=user,
            team__workspace__slug=workspace_slug,
            deleted_at__isnull=True,
        ).values_list("team_id", flat=True)
    )


def get_teamspace_project_ids(user, workspace_slug):
    """Get all project IDs the user has access to through teamspace membership."""
    member_teamspace_ids = get_teamspace_member_ids(user, workspace_slug)

    if not member_teamspace_ids:
        return []

    return list(
        TeamspaceProject.objects.filter(
            team_id__in=member_teamspace_ids,
            deleted_at__isnull=True,
        ).values_list("project_id", flat=True)
    )


def filter_by_teamspace(user, workspace_slug, queryset, project_field="project"):
    """
    Filter queryset to only include projects the user has access to through teamspace membership.

    For workspace-level visibility teamspaces, all workspace members have access.
    For private teamspaces, only teamspace members have access.

    Args:
        user: The user object
        workspace_slug: The workspace slug
        queryset: The queryset to filter
        project_field: The field name for the project in the queryset

    Returns:
        Filtered queryset
    """
    from plane.db.models import WorkspaceMember, Team

    is_workspace_member = WorkspaceMember.objects.filter(
        workspace__slug=workspace_slug,
        member=user,
        is_active=True,
    ).exists()

    if is_workspace_member:
        return queryset

    private_teamspace_project_ids = get_teamspace_project_ids(user, workspace_slug)

    if private_teamspace_project_ids:
        return queryset.filter(**{f"{project_field}__id__in": private_teamspace_project_ids})

    return queryset.none()
