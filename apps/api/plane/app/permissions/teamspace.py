# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Third Party imports
from rest_framework.permissions import BasePermission, SAFE_METHODS

# Module imports
from plane.db.models import WorkspaceMember, TeamspaceMember


class TeamspacePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        workspace_slug = view.kwargs.get("slug")
        teamspace_id = view.kwargs.get("teamspace_id")

        if not workspace_slug:
            return False

        workspace_member = WorkspaceMember.objects.filter(
            workspace__slug=workspace_slug,
            member=request.user,
            is_active=True,
        ).exists()

        if not workspace_member:
            return False

        if request.method in SAFE_METHODS:
            return True

        if teamspace_id:
            teamspace_member = TeamspaceMember.objects.filter(
                team_id=teamspace_id,
                member=request.user,
            ).first()

            if teamspace_member:
                return teamspace_member.role in ["admin", "member"]

        return workspace_member


class TeamspaceAdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        workspace_slug = view.kwargs.get("slug")
        teamspace_id = view.kwargs.get("teamspace_id")

        if not workspace_slug:
            return False

        workspace_member = WorkspaceMember.objects.filter(
            workspace__slug=workspace_slug,
            member=request.user,
            role__in=[20, 15],
            is_active=True,
        ).exists()

        if not workspace_member:
            return False

        if teamspace_id:
            teamspace_member = TeamspaceMember.objects.filter(
                team_id=teamspace_id,
                member=request.user,
                role="admin",
            ).exists()

            if teamspace_member:
                return True

        return workspace_member
