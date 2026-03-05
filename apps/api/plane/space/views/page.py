# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.db.models import Q, Prefetch

# Third Party imports
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# Module imports
from .base import BaseAPIView
from plane.db.models import Page, ProjectPage, DeployBoard


class PageRetrievePublicEndpoint(BaseAPIView):
    permission_classes = [AllowAny]

    def get(self, request, project_id, page_id):
        try:
            deploy_board = DeployBoard.objects.get(entity_identifier=project_id, entity_name="project")
        except DeployBoard.DoesNotExist:
            return Response({"error": "Project is not published"}, status=status.HTTP_404_NOT_FOUND)

        if deploy_board.is_disabled:
            return Response({"error": "Project is not published"}, status=status.HTTP_404_NOT_FOUND)

        page_queryset = (
            Page.objects.filter(
                pk=page_id,
                workspace_id=deploy_board.workspace_id,
                project_pages__project_id=project_id,
                project_pages__deleted_at__isnull=True,
            )
            .select_related("workspace", "owned_by")
            .prefetch_related(
                Prefetch(
                    "child_page",
                    queryset=Page.objects.filter(
                        workspace_id=deploy_board.workspace_id,
                        project_pages__project_id=project_id,
                        project_pages__deleted_at__isnull=True,
                    )
                    .select_related("workspace", "owned_by")
                    .prefetch_related(
                        Prefetch(
                            "child_page",
                            queryset=Page.objects.filter(
                                workspace_id=deploy_board.workspace_id,
                                project_pages__project_id=project_id,
                                project_pages__deleted_at__isnull=True,
                            ).select_related("workspace", "owned_by"),
                        )
                    ),
                )
            )
        ).first()

        if not page_queryset:
            return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)

        page_data = {
            "id": page_queryset.id,
            "name": page_queryset.name,
            "description_json": page_queryset.description_json,
            "description_html": page_queryset.description_html,
            "description_stripped": page_queryset.description_stripped,
            "color": page_queryset.color,
            "is_locked": page_queryset.is_locked,
            "created_at": page_queryset.created_at,
            "updated_at": page_queryset.updated_at,
            "owned_by": {
                "id": page_queryset.owned_by.id,
                "first_name": page_queryset.owned_by.first_name,
                "last_name": page_queryset.owned_by.last_name,
                "avatar": page_queryset.owned_by.avatar,
                "avatar_url": page_queryset.owned_by.avatar_url,
            }
            if page_queryset.owned_by
            else None,
            "sub_pages": self._serialize_sub_pages(page_queryset.child_page.all())
            if hasattr(page_queryset, "child_page")
            else [],
        }

        return Response({"page": page_data}, status=status.HTTP_200_OK)

    def _serialize_sub_pages(self, sub_pages):
        result = []
        for sub_page in sub_pages:
            sub_page_data = {
                "id": sub_page.id,
                "name": sub_page.name,
                "description_json": sub_page.description_json,
                "description_html": sub_page.description_html,
                "description_stripped": sub_page.description_stripped,
                "color": sub_page.color,
                "is_locked": sub_page.is_locked,
                "created_at": sub_page.created_at,
                "updated_at": sub_page.updated_at,
                "owned_by": {
                    "id": sub_page.owned_by.id,
                    "first_name": sub_page.owned_by.first_name,
                    "last_name": sub_page.owned_by.last_name,
                    "avatar": sub_page.owned_by.avatar,
                    "avatar_url": sub_page.owned_by.avatar_url,
                }
                if sub_page.owned_by
                else None,
            }

            if hasattr(sub_page, "child_page"):
                children = sub_page.child_page.all()
                if children:
                    sub_page_data["sub_pages"] = self._serialize_sub_pages(children)

            result.append(sub_page_data)

        return result
