# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import json

# Django imports
from django.utils import timezone
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder

# Third Party imports
from rest_framework.response import Response
from rest_framework import status

# Module imports
from .. import BaseViewSet
from plane.app.serializers import IssueHierarchyLinkSerializer
from plane.app.permissions import ProjectEntityPermission
from plane.db.models import IssueHierarchyLink, Issue, Project
from plane.bgtasks.issue_activities_task import issue_activity
from plane.utils.host import base_host


class IssueHierarchyLinkViewSet(BaseViewSet):
    serializer_class = IssueHierarchyLinkSerializer
    model = IssueHierarchyLink
    permission_classes = [ProjectEntityPermission]

    def get_queryset(self):
        return IssueHierarchyLink.objects.filter(
            Q(project_id=self.kwargs.get("project_id"))
            | Q(parent_issue__project_id=self.kwargs.get("project_id"))
            | Q(child_issue__project_id=self.kwargs.get("project_id"))
        ).filter(workspace__slug=self.kwargs.get("slug"))

    def list(self, request, slug, project_id, issue_id):
        hierarchy_links = IssueHierarchyLink.objects.filter(
            Q(parent_issue_id=issue_id) | Q(child_issue_id=issue_id)
        ).filter(workspace__slug=slug, project_id=project_id)

        return Response(
            IssueHierarchyLinkSerializer(hierarchy_links, many=True).data,
            status=status.HTTP_200_OK,
        )

    def create(self, request, slug, project_id, issue_id):
        child_issue_id = request.data.get("child_issue_id")

        if not child_issue_id:
            return Response(
                {"error": "child_issue_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if str(child_issue_id) == str(issue_id):
            return Response(
                {"error": "Cannot link an issue to itself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            parent_issue = Issue.objects.get(pk=issue_id)
            child_issue = Issue.objects.get(pk=child_issue_id)
        except Issue.DoesNotExist:
            return Response(
                {"error": "Issue not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if parent_issue.project_id != child_issue.project_id:
            return Response(
                {"error": "Parent and child issues must be in the same project"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if parent_issue.workspace_id != child_issue.workspace_id:
            return Response(
                {"error": "Parent and child issues must be in the same workspace"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self._would_create_cycle(parent_issue, child_issue):
            return Response(
                {"error": "Cannot create circular hierarchy link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_link = IssueHierarchyLink.objects.filter(
            parent_issue_id=issue_id,
            child_issue_id=child_issue_id,
            deleted_at__isnull=True,
        ).first()

        if existing_link:
            return Response(
                {"error": "This hierarchy link already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = Project.objects.get(pk=project_id)

        hierarchy_link = IssueHierarchyLink.objects.create(
            parent_issue_id=issue_id,
            child_issue_id=child_issue_id,
            project_id=project_id,
            workspace_id=project.workspace_id,
            created_by=request.user,
            updated_by=request.user,
        )

        calculate_issue_rollups(issue_id)

        issue_activity.delay(
            type="issue_hierarchy_link.activity.created",
            requested_data=json.dumps(request.data, cls=DjangoJSONEncoder),
            actor_id=str(request.user.id),
            issue_id=str(issue_id),
            project_id=str(project_id),
            current_instance=None,
            epoch=int(timezone.now().timestamp()),
            notification=True,
            origin=base_host(request=request, is_app=True),
        )

        return Response(
            IssueHierarchyLinkSerializer(hierarchy_link).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, slug, project_id, issue_id, pk):
        try:
            hierarchy_link = IssueHierarchyLink.objects.get(pk=pk)
        except IssueHierarchyLink.DoesNotExist:
            return Response(
                {"error": "Hierarchy link not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        current_instance = json.dumps(IssueHierarchyLinkSerializer(hierarchy_link).data, cls=DjangoJSONEncoder)
        parent_issue_id = hierarchy_link.parent_issue_id
        hierarchy_link.delete()

        calculate_issue_rollups(parent_issue_id)

        issue_activity.delay(
            type="issue_hierarchy_link.activity.deleted",
            requested_data=json.dumps({"link_id": str(pk)}, cls=DjangoJSONEncoder),
            actor_id=str(request.user.id),
            issue_id=str(issue_id),
            project_id=str(project_id),
            current_instance=current_instance,
            epoch=int(timezone.now().timestamp()),
            notification=True,
            origin=base_host(request=request, is_app=True),
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _would_create_cycle(self, parent_issue, child_issue):
        """
        Check if creating a link from parent_issue to child_issue would create a cycle.
        A cycle would occur if child_issue is already an ancestor of parent_issue.
        """
        visited = set()
        queue = [child_issue.id]

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id == parent_issue.id:
                return True

            links = IssueHierarchyLink.objects.filter(parent_issue_id=current_id, deleted_at__isnull=True).values_list(
                "child_issue_id", flat=True
            )

            queue.extend(links)

        return False
