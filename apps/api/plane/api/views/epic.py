# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import json

# Django imports
from django.core import serializers
from django.db.models import Count, F, Func, OuterRef, Prefetch, Q
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

# Third party imports
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, OpenApiRequest

# Module imports
from plane.api.serializers import (
    IssueSerializer,
    EpicIssueSerializer,
    EpicSerializer,
    EpicIssueRequestSerializer,
    EpicCreateSerializer,
    EpicUpdateSerializer,
    EpicLinkSerializer,
    InitiativeSerializer,
    InitiativeCreateSerializer,
    InitiativeUpdateSerializer,
    InitiativeLinkSerializer,
)
from plane.app.permissions import ProjectEntityPermission
from plane.bgtasks.issue_activities_task import issue_activity
from plane.db.models import (
    Issue,
    FileAsset,
    IssueLink,
    Epic,
    EpicIssue,
    EpicLink,
    Initiative,
    InitiativeEpic,
    InitiativeLink,
    Project,
    ProjectMember,
    UserFavorite,
)

from .base import BaseAPIView
from plane.bgtasks.webhook_task import model_activity
from plane.utils.host import base_host
from plane.utils.openapi import create_paginated_response


class InitiativeListCreateAPIEndpoint(BaseAPIView):
    """Initiative List and Create Endpoint"""

    serializer_class = InitiativeSerializer
    model = Initiative
    webhook_event = "initiative"
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return (
            Initiative.objects.filter(project_id=self.kwargs.get("project_id"))
            .filter(workspace__slug=self.kwargs.get("slug"))
            .select_related("project")
            .select_related("workspace")
            .select_related("lead")
            .prefetch_related("members")
            .prefetch_related(
                Prefetch(
                    "link_initiative",
                    queryset=InitiativeLink.objects.select_related("initiative", "created_by"),
                )
            )
            .annotate(
                total_epics=Count(
                    "epics",
                    filter=Q(
                        epics__archived_at__isnull=True,
                        epics__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                completed_epics=Count(
                    "epics__status",
                    filter=Q(
                        epics__status="completed",
                        epics__archived_at__isnull=True,
                        epics__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                started_epics=Count(
                    "epics__status",
                    filter=Q(
                        epics__status="in-progress",
                        epics__archived_at__isnull=True,
                        epics__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                backlog_epics=Count(
                    "epics__status",
                    filter=Q(
                        epics__status="backlog",
                        epics__archived_at__isnull=True,
                        epics__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                cancelled_epics=Count(
                    "epics__status",
                    filter=Q(
                        epics__status="cancelled",
                        epics__archived_at__isnull=True,
                        epics__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .order_by(self.kwargs.get("order_by", "-created_at"))
        )

    def post(self, request, slug, project_id):
        """Create initiative"""
        project = Project.objects.get(pk=project_id, workspace__slug=slug)
        serializer = InitiativeCreateSerializer(
            data=request.data,
            context={"project_id": project_id, "workspace_id": project.workspace_id},
        )
        if serializer.is_valid():
            if (
                request.data.get("external_id")
                and request.data.get("external_source")
                and Initiative.objects.filter(
                    project_id=project_id,
                    workspace__slug=slug,
                    external_source=request.data.get("external_source"),
                    external_id=request.data.get("external_id"),
                ).exists()
            ):
                initiative = Initiative.objects.filter(
                    project_id=project_id,
                    workspace__slug=slug,
                    external_source=request.data.get("external_source"),
                    external_id=request.data.get("external_id"),
                ).first()
                return Response(
                    {
                        "error": "Initiative with the same external id and external source already exists",
                        "id": str(initiative.id),
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            serializer.save()
            model_activity.delay(
                model_name="initiative",
                model_id=str(serializer.instance.id),
                requested_data=request.data,
                current_instance=None,
                actor_id=request.user.id,
                slug=slug,
                origin=base_host(request=request, is_app=True),
            )
            initiative = Initiative.objects.get(pk=serializer.instance.id)
            serializer = InitiativeSerializer(initiative)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, slug, project_id):
        """List or retrieve initiatives"""
        return self.paginate(
            request=request,
            queryset=(self.get_queryset().filter(archived_at__isnull=True)),
            on_results=lambda initiatives: (
                InitiativeSerializer(initiatives, many=True, fields=self.fields, expand=self.expand).data
            ),
        )


class InitiativeDetailAPIEndpoint(BaseAPIView):
    """Initiative Detail Endpoint"""

    model = Initiative
    permission_classes = [ProjectEntityPermission]
    serializer_class = InitiativeSerializer
    webhook_event = "initiative"
    use_read_replica = True

    def get_queryset(self):
        return (
            Initiative.objects.filter(project_id=self.kwargs.get("project_id"))
            .filter(workspace__slug=self.kwargs.get("slug"))
            .select_related("project")
            .select_related("workspace")
            .select_related("lead")
            .prefetch_related("members")
            .prefetch_related(
                Prefetch(
                    "link_initiative",
                    queryset=InitiativeLink.objects.select_related("initiative", "created_by"),
                )
            )
            .annotate(
                total_epics=Count(
                    "epics",
                    filter=Q(
                        epics__archived_at__isnull=True,
                        epics__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                completed_epics=Count(
                    "epics__status",
                    filter=Q(
                        epics__status="completed",
                        epics__archived_at__isnull=True,
                        epics__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .order_by(self.kwargs.get("order_by", "-created_at"))
        )

    def patch(self, request, slug, project_id, pk):
        """Update initiative"""
        initiative = Initiative.objects.get(pk=pk, project_id=project_id, workspace__slug=slug)

        current_instance = json.dumps(InitiativeSerializer(initiative).data, cls=DjangoJSONEncoder)

        if initiative.archived_at:
            return Response(
                {"error": "Archived initiative cannot be edited"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = InitiativeUpdateSerializer(
            initiative, data=request.data, context={"project_id": project_id}, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            model_activity.delay(
                model_name="initiative",
                model_id=str(serializer.instance.id),
                requested_data=request.data,
                current_instance=current_instance,
                actor_id=request.user.id,
                slug=slug,
                origin=base_host(request=request, is_app=True),
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, slug, project_id, pk):
        """Retrieve initiative"""
        queryset = self.get_queryset().filter(archived_at__isnull=True).get(pk=pk)
        data = InitiativeSerializer(queryset, fields=self.fields, expand=self.expand).data
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, slug, project_id, pk):
        """Delete initiative"""
        initiative = Initiative.objects.get(workspace__slug=slug, project_id=project_id, pk=pk)
        if initiative.created_by_id != request.user.id and (
            not ProjectMember.objects.filter(
                workspace__slug=slug,
                member=request.user,
                role=20,
                project_id=project_id,
                is_active=True,
            ).exists()
        ):
            return Response(
                {"error": "Only admin or creator can delete the initiative"},
                status=status.HTTP_403_FORBIDDEN,
            )

        initiative_epics = list(InitiativeEpic.objects.filter(initiative_id=pk).values_list("epic", flat=True))
        initiative.delete()
        InitiativeEpic.objects.filter(initiative=pk, project_id=project_id).delete()
        UserFavorite.objects.filter(entity_type="initiative", entity_identifier=pk, project_id=project_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EpicListCreateAPIEndpoint(BaseAPIView):
    """Epic List and Create Endpoint"""

    serializer_class = EpicSerializer
    model = Epic
    webhook_event = "epic"
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return (
            Epic.objects.filter(project_id=self.kwargs.get("project_id"))
            .filter(workspace__slug=self.kwargs.get("slug"))
            .select_related("project")
            .select_related("workspace")
            .select_related("lead")
            .select_related("initiative")
            .prefetch_related("members")
            .prefetch_related(
                Prefetch(
                    "link_epic",
                    queryset=EpicLink.objects.select_related("epic", "created_by"),
                )
            )
            .annotate(
                total_issues=Count(
                    "epic_issues",
                    filter=Q(
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                completed_issues=Count(
                    "epic_issues__issue__state__group",
                    filter=Q(
                        epic_issues__issue__state__group="completed",
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                cancelled_issues=Count(
                    "epic_issues__issue__state__group",
                    filter=Q(
                        epic_issues__issue__state__group="cancelled",
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                started_issues=Count(
                    "epic_issues__issue__state__group",
                    filter=Q(
                        epic_issues__issue__state__group="started",
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                unstarted_issues=Count(
                    "epic_issues__issue__state__group",
                    filter=Q(
                        epic_issues__issue__state__group="unstarted",
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                backlog_issues=Count(
                    "epic_issues__issue__state__group",
                    filter=Q(
                        epic_issues__issue__state__group="backlog",
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .order_by(self.kwargs.get("order_by", "-created_at"))
        )

    def post(self, request, slug, project_id):
        """Create epic"""
        project = Project.objects.get(pk=project_id, workspace__slug=slug)
        serializer = EpicCreateSerializer(
            data=request.data,
            context={"project_id": project_id, "workspace_id": project.workspace_id},
        )
        if serializer.is_valid():
            if (
                request.data.get("external_id")
                and request.data.get("external_source")
                and Epic.objects.filter(
                    project_id=project_id,
                    workspace__slug=slug,
                    external_source=request.data.get("external_source"),
                    external_id=request.data.get("external_id"),
                ).exists()
            ):
                epic = Epic.objects.filter(
                    project_id=project_id,
                    workspace__slug=slug,
                    external_source=request.data.get("external_source"),
                    external_id=request.data.get("external_id"),
                ).first()
                return Response(
                    {
                        "error": "Epic with the same external id and external source already exists",
                        "id": str(epic.id),
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            serializer.save()
            model_activity.delay(
                model_name="epic",
                model_id=str(serializer.instance.id),
                requested_data=request.data,
                current_instance=None,
                actor_id=request.user.id,
                slug=slug,
                origin=base_host(request=request, is_app=True),
            )
            epic = Epic.objects.get(pk=serializer.instance.id)
            serializer = EpicSerializer(epic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, slug, project_id):
        """List or retrieve epics"""
        return self.paginate(
            request=request,
            queryset=(self.get_queryset().filter(archived_at__isnull=True)),
            on_results=lambda epics: EpicSerializer(epics, many=True, fields=self.fields, expand=self.expand).data,
        )


class EpicDetailAPIEndpoint(BaseAPIView):
    """Epic Detail Endpoint"""

    model = Epic
    permission_classes = [ProjectEntityPermission]
    serializer_class = EpicSerializer
    webhook_event = "epic"
    use_read_replica = True

    def get_queryset(self):
        return (
            Epic.objects.filter(project_id=self.kwargs.get("project_id"))
            .filter(workspace__slug=self.kwargs.get("slug"))
            .select_related("project")
            .select_related("workspace")
            .select_related("lead")
            .select_related("initiative")
            .prefetch_related("members")
            .prefetch_related(
                Prefetch(
                    "link_epic",
                    queryset=EpicLink.objects.select_related("epic", "created_by"),
                )
            )
            .annotate(
                total_issues=Count(
                    "epic_issues",
                    filter=Q(
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                completed_issues=Count(
                    "epic_issues__issue__state__group",
                    filter=Q(
                        epic_issues__issue__state__group="completed",
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                cancelled_issues=Count(
                    "epic_issues__issue__state__group",
                    filter=Q(
                        epic_issues__issue__state__group="cancelled",
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                started_issues=Count(
                    "epic_issues__issue__state__group",
                    filter=Q(
                        epic_issues__issue__state__group="started",
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                unstarted_issues=Count(
                    "epic_issues__issue__state__group",
                    filter=Q(
                        epic_issues__issue__state__group="unstarted",
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .annotate(
                backlog_issues=Count(
                    "epic_issues__issue__state__group",
                    filter=Q(
                        epic_issues__issue__state__group="backlog",
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .order_by(self.kwargs.get("order_by", "-created_at"))
        )

    def patch(self, request, slug, project_id, pk):
        """Update epic"""
        epic = Epic.objects.get(pk=pk, project_id=project_id, workspace__slug=slug)

        current_instance = json.dumps(EpicSerializer(epic).data, cls=DjangoJSONEncoder)

        if epic.archived_at:
            return Response(
                {"error": "Archived epic cannot be edited"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = EpicUpdateSerializer(epic, data=request.data, context={"project_id": project_id}, partial=True)
        if serializer.is_valid():
            serializer.save()
            model_activity.delay(
                model_name="epic",
                model_id=str(serializer.instance.id),
                requested_data=request.data,
                current_instance=current_instance,
                actor_id=request.user.id,
                slug=slug,
                origin=base_host(request=request, is_app=True),
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, slug, project_id, pk):
        """Retrieve epic"""
        queryset = self.get_queryset().filter(archived_at__isnull=True).get(pk=pk)
        data = EpicSerializer(queryset, fields=self.fields, expand=self.expand).data
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, slug, project_id, pk):
        """Delete epic"""
        epic = Epic.objects.get(workspace__slug=slug, project_id=project_id, pk=pk)
        if epic.created_by_id != request.user.id and (
            not ProjectMember.objects.filter(
                workspace__slug=slug,
                member=request.user,
                role=20,
                project_id=project_id,
                is_active=True,
            ).exists()
        ):
            return Response(
                {"error": "Only admin or creator can delete the epic"},
                status=status.HTTP_403_FORBIDDEN,
            )

        epic_issues = list(EpicIssue.objects.filter(epic_id=pk).values_list("issue", flat=True))
        epic.delete()
        EpicIssue.objects.filter(epic=pk, project_id=project_id).delete()
        UserFavorite.objects.filter(entity_type="epic", entity_identifier=pk, project_id=project_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EpicIssueListCreateAPIEndpoint(BaseAPIView):
    """Epic Work Item List and Create Endpoint"""

    serializer_class = EpicIssueSerializer
    model = EpicIssue
    webhook_event = "epic_issue"
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return (
            EpicIssue.objects.annotate(
                sub_issues_count=Issue.issue_objects.filter(parent=OuterRef("issue"))
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .filter(workspace__slug=self.kwargs.get("slug"))
            .filter(project_id=self.kwargs.get("project_id"))
            .filter(epic_id=self.kwargs.get("epic_id"))
            .filter(
                project__project_projectmember__member=self.request.user,
                project__project_projectmember__is_active=True,
            )
            .filter(project__archived_at__isnull=True)
            .select_related("project")
            .select_related("workspace")
            .select_related("epic")
            .select_related("issue", "issue__state", "issue__project")
            .prefetch_related("issue__assignees", "issue__labels")
            .prefetch_related("epic__members")
            .order_by(self.kwargs.get("order_by", "-created_at"))
            .distinct()
        )

    def get(self, request, slug, project_id, epic_id):
        """List epic work items"""
        order_by = request.GET.get("order_by", "created_at")
        issues = (
            Issue.issue_objects.filter(issue_epic__epic_id=epic_id, issue_epic__deleted_at__isnull=True)
            .annotate(
                sub_issues_count=Issue.issue_objects.filter(parent=OuterRef("id"))
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(bridge_id=F("issue_epic__id"))
            .filter(project_id=project_id)
            .filter(workspace__slug=slug)
            .select_related("project")
            .select_related("workspace")
            .select_related("state")
            .select_related("parent")
            .prefetch_related("assignees")
            .prefetch_related("labels")
            .order_by(order_by)
            .annotate(
                link_count=IssueLink.objects.filter(issue=OuterRef("id"))
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(
                attachment_count=FileAsset.objects.filter(
                    issue_id=OuterRef("id"),
                    entity_type=FileAsset.EntityTypeContext.ISSUE_ATTACHMENT,
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
        )
        return self.paginate(
            request=request,
            queryset=(issues),
            on_results=lambda issues: IssueSerializer(issues, many=True, fields=self.fields, expand=self.expand).data,
        )

    def post(self, request, slug, project_id, epic_id):
        """Add epic work items"""
        issues = request.data.get("issues", [])
        if not len(issues):
            return Response({"error": "Issues are required"}, status=status.HTTP_400_BAD_REQUEST)
        epic = Epic.objects.get(workspace__slug=slug, project_id=project_id, pk=epic_id)

        issues = Issue.objects.filter(workspace__slug=slug, project_id=project_id, pk__in=issues).values_list(
            "id", flat=True
        )

        epic_issues = list(EpicIssue.objects.filter(issue_id__in=issues))

        update_epic_issue_activity = []
        records_to_update = []
        record_to_create = []

        for issue in issues:
            epic_issue = [ei for ei in epic_issues if str(ei.issue_id) in issues]

            if len(epic_issue):
                if epic_issue[0].epic_id != epic_id:
                    update_epic_issue_activity.append(
                        {
                            "old_epic_id": str(epic_issue[0].epic_id),
                            "new_epic_id": str(epic_id),
                            "issue_id": str(epic_issue[0].issue_id),
                        }
                    )
                    epic_issue[0].epic_id = epic_id
                    records_to_update.append(epic_issue[0])
            else:
                record_to_create.append(
                    EpicIssue(
                        epic=epic,
                        issue_id=issue,
                        project_id=project_id,
                        workspace=epic.workspace,
                        created_by=request.user,
                        updated_by=request.user,
                    )
                )

        EpicIssue.objects.bulk_create(record_to_create, batch_size=10, ignore_conflicts=True)

        EpicIssue.objects.bulk_update(records_to_update, ["epic"], batch_size=10)

        issue_activity.delay(
            type="epic.activity.created",
            requested_data=json.dumps({"epics_list": str(issues)}),
            actor_id=str(self.request.user.id),
            issue_id=None,
            project_id=str(self.kwargs.get("project_id", None)),
            current_instance=json.dumps(
                {
                    "updated_epic_issues": update_epic_issue_activity,
                    "created_epic_issues": serializers.serialize("json", record_to_create),
                }
            ),
            epoch=int(timezone.now().timestamp()),
            origin=base_host(request=request, is_app=True),
        )

        return Response(
            EpicIssueSerializer(self.get_queryset(), many=True).data,
            status=status.HTTP_200_OK,
        )


class EpicIssueDetailAPIEndpoint(BaseAPIView):
    """Epic Work Item Detail Endpoint"""

    serializer_class = EpicIssueSerializer
    model = EpicIssue
    webhook_event = "epic_issue"
    bulk = True
    use_read_replica = True
    permission_classes = [ProjectEntityPermission]

    def get_queryset(self):
        return (
            EpicIssue.objects.annotate(
                sub_issues_count=Issue.issue_objects.filter(parent=OuterRef("issue"))
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .filter(workspace__slug=self.kwargs.get("slug"))
            .filter(project_id=self.kwargs.get("project_id"))
            .filter(epic_id=self.kwargs.get("epic_id"))
            .filter(
                project__project_projectmember__member=self.request.user,
                project__project_projectmember__is_active=True,
            )
            .filter(project__archived_at__isnull=True)
            .select_related("project")
            .select_related("workspace")
            .select_related("epic")
            .select_related("issue", "issue__state", "issue__project")
            .prefetch_related("issue__assignees", "issue__labels")
            .prefetch_related("epic__members")
            .order_by(self.kwargs.get("order_by", "-created_at"))
            .distinct()
        )

    def delete(self, request, slug, project_id, epic_id, issue_id):
        """Remove epic work item"""
        epic_issue = EpicIssue.objects.get(
            workspace__slug=slug,
            project_id=project_id,
            epic_id=epic_id,
            issue_id=issue_id,
        )

        epic_name = epic_issue.epic.name if epic_issue.epic is not None else ""
        epic_issue.delete()
        issue_activity.delay(
            type="epic.activity.deleted",
            requested_data=json.dumps({"epic_id": str(epic_id), "issues": [str(epic_issue.issue_id)]}),
            actor_id=str(request.user.id),
            issue_id=str(issue_id),
            project_id=str(project_id),
            current_instance=json.dumps({"epic_name": epic_name}),
            epoch=int(timezone.now().timestamp()),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class EpicArchiveUnarchiveAPIEndpoint(BaseAPIView):
    """Epic Archive and Unarchive Endpoint"""

    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return (
            Epic.objects.filter(project_id=self.kwargs.get("project_id"))
            .filter(workspace__slug=self.kwargs.get("slug"))
            .filter(archived_at__isnull=False)
            .select_related("project")
            .select_related("workspace")
            .select_related("lead")
            .select_related("initiative")
            .prefetch_related("members")
            .annotate(
                total_issues=Count(
                    "epic_issues",
                    filter=Q(
                        epic_issues__issue__archived_at__isnull=True,
                        epic_issues__issue__is_draft=False,
                        epic_issues__deleted_at__isnull=True,
                    ),
                    distinct=True,
                )
            )
            .order_by(self.kwargs.get("order_by", "-created_at"))
        )

    def get(self, request, slug, project_id):
        """List archived epics"""
        return self.paginate(
            request=request,
            queryset=(self.get_queryset()),
            on_results=lambda epics: EpicSerializer(epics, many=True, fields=self.fields, expand=self.expand).data,
        )

    def post(self, request, slug, project_id, pk):
        """Archive epic"""
        epic = Epic.objects.get(pk=pk, project_id=project_id, workspace__slug=slug)
        if epic.status not in ["completed", "cancelled"]:
            return Response(
                {"error": "Only completed or cancelled epics can be archived"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        epic.archived_at = timezone.now()
        epic.save()
        UserFavorite.objects.filter(
            entity_type="epic",
            entity_identifier=pk,
            project_id=project_id,
            workspace__slug=slug,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, slug, project_id, pk):
        """Unarchive epic"""
        epic = Epic.objects.get(pk=pk, project_id=project_id, workspace__slug=slug)
        epic.archived_at = None
        epic.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
