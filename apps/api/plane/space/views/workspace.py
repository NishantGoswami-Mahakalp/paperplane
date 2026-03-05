# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.db.models import Count, Q, Exists, OuterRef, F, Func

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .base import BaseAPIView
from plane.db.models import Workspace, Project, DeployBoard, ProjectMember, Issue
from plane.space.serializer.workspace import WorkspacePublicSerializer, PublicProjectSerializer


class WorkspacePublicEndpoint(BaseAPIView):
    permission_classes = [AllowAny]

    def get(self, request, workspace_id):
        workspace = Workspace.objects.filter(id=workspace_id).first()

        if not workspace:
            return Response(
                {"error": "Workspace not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        has_public_projects = Project.objects.filter(
            workspace=workspace,
            network=2,
        ).exists()

        if not has_public_projects:
            return Response(
                {"error": "Workspace is not public"},
                status=status.HTTP_404_NOT_FOUND,
            )

        projects = (
            Project.objects.filter(
                workspace=workspace,
                network=2,
            )
            .annotate(
                member_count=ProjectMember.objects.filter(
                    project_id=OuterRef("id"),
                    is_active=True,
                    member__is_bot=False,
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(
                issue_count=Issue.issue_objects.filter(
                    project_id=OuterRef("id"),
                    archived_at__isnull=True,
                    is_draft=False,
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(
                anchor=DeployBoard.objects.filter(
                    project_id=OuterRef("id"),
                    entity_name="project",
                ).values("anchor")[:1]
            )
            .annotate(
                is_comments_enabled=DeployBoard.objects.filter(
                    project_id=OuterRef("id"),
                    entity_name="project",
                ).values("is_comments_enabled")[:1]
            )
            .annotate(
                is_reactions_enabled=DeployBoard.objects.filter(
                    project_id=OuterRef("id"),
                    entity_name="project",
                ).values("is_reactions_enabled")[:1]
            )
            .annotate(
                is_votes_enabled=DeployBoard.objects.filter(
                    project_id=OuterRef("id"),
                    entity_name="project",
                ).values("is_votes_enabled")[:1]
            )
            .distinct()
        )

        workspace_serializer = WorkspacePublicSerializer(workspace)
        projects_serializer = PublicProjectSerializer(projects, many=True)

        return Response(
            {
                "workspace": workspace_serializer.data,
                "projects": projects_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
