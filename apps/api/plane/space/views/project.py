# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.db.models import Exists, OuterRef, Func, F, Q, Prefetch, Subquery

# Third Party imports
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# Module imports
from .base import BaseAPIView
from .issue import ProjectIssuesPublicEndpoint
from plane.app.serializers import DeployBoardSerializer
from plane.db.models import (
    Project,
    DeployBoard,
    ProjectMember,
    Issue,
    IssueReaction,
    IssueVote,
    CycleIssue,
    IssueLink,
    FileAsset,
)
from plane.utils.issue_filters import issue_filters
from plane.utils.order_queryset import order_issue_queryset
from plane.space.utils.grouper import (
    issue_group_values,
    issue_on_results,
    issue_queryset_grouper,
)
from plane.utils.paginator import GroupedOffsetPaginator, SubGroupedOffsetPaginator


class ProjectDeployBoardPublicSettingsEndpoint(BaseAPIView):
    permission_classes = [AllowAny]

    def get(self, request, anchor):
        project_deploy_board = DeployBoard.objects.get(anchor=anchor, entity_name="project")
        serializer = DeployBoardSerializer(project_deploy_board)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkspaceProjectDeployBoardEndpoint(BaseAPIView):
    permission_classes = [AllowAny]

    def get(self, request, anchor):
        deploy_board = DeployBoard.objects.filter(anchor=anchor, entity_name="project").values_list
        projects = (
            Project.objects.filter(workspace=deploy_board.workspace)
            .annotate(
                is_public=Exists(
                    DeployBoard.objects.filter(anchor=anchor, project_id=OuterRef("pk"), entity_name="project")
                )
            )
            .filter(is_public=True)
        ).values(
            "id",
            "identifier",
            "name",
            "description",
            "emoji",
            "icon_prop",
            "cover_image",
        )

        return Response(projects, status=status.HTTP_200_OK)


class WorkspaceProjectAnchorEndpoint(BaseAPIView):
    permission_classes = [AllowAny]

    def get(self, request, slug, project_id):
        project_deploy_board = DeployBoard.objects.get(
            workspace__slug=slug, project_id=project_id, entity_name="project"
        )
        serializer = DeployBoardSerializer(project_deploy_board)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectMembersEndpoint(BaseAPIView):
    permission_classes = [AllowAny]

    def get(self, request, anchor):
        deploy_board = DeployBoard.objects.filter(anchor=anchor).first()
        if not deploy_board:
            return Response(
                {"error": "Invalid anchor"},
                status=status.HTTP_404_NOT_FOUND,
            )

        members = ProjectMember.objects.filter(
            project=deploy_board.project,
            workspace=deploy_board.workspace,
            is_active=True,
        ).values(
            "id",
            "member",
            "member__display_name",
            "member__avatar",
        )
        return Response(members, status=status.HTTP_200_OK)


class ProjectBoardPublicEndpoint(BaseAPIView):
    permission_classes = [AllowAny]

    def get(self, request, anchor):
        deploy_board = DeployBoard.objects.filter(anchor=anchor, entity_name="project").first()
        if not deploy_board:
            return Response(
                {"error": "Project is not published"},
                status=status.HTTP_404_NOT_FOUND,
            )

        project_id = deploy_board.entity_identifier
        slug = deploy_board.workspace.slug

        settings_serializer = DeployBoardSerializer(deploy_board)

        filters = issue_filters(request.query_params, "GET")
        order_by_param = request.GET.get("order_by", "-created_at")

        issue_queryset = (
            Issue.issue_objects.filter(workspace__slug=slug, project_id=project_id)
            .select_related("workspace", "project", "state", "parent")
            .prefetch_related("assignees", "labels", "issue_module__module")
            .prefetch_related(
                Prefetch(
                    "issue_reactions",
                    queryset=IssueReaction.objects.select_related("actor"),
                )
            )
            .prefetch_related(Prefetch("votes", queryset=IssueVote.objects.select_related("actor")))
            .annotate(
                cycle_id=Subquery(
                    CycleIssue.objects.filter(issue=OuterRef("id"), deleted_at__isnull=True).values("cycle_id")[:1]
                )
            )
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
            .annotate(
                sub_issues_count=Issue.issue_objects.filter(parent=OuterRef("id"))
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
        ).distinct()

        issue_queryset = issue_queryset.filter(**filters)

        issue_queryset, order_by_param = order_issue_queryset(
            issue_queryset=issue_queryset, order_by_param=order_by_param
        )

        group_by = request.GET.get("group_by", False)
        sub_group_by = request.GET.get("sub_group_by", False)

        issue_queryset = issue_queryset_grouper(queryset=issue_queryset, group_by=group_by, sub_group_by=sub_group_by)

        if group_by:
            if sub_group_by:
                if group_by == sub_group_by:
                    return Response(
                        {"error": "Group by and sub group by cannot have same parameters"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    issues = self.paginate(
                        request=request,
                        order_by=order_by_param,
                        queryset=issue_queryset,
                        on_results=lambda issues: issue_on_results(
                            group_by=group_by, issues=issues, sub_group_by=sub_group_by
                        ),
                        paginator_cls=SubGroupedOffsetPaginator,
                        group_by_fields=issue_group_values(
                            field=group_by,
                            slug=slug,
                            project_id=project_id,
                            filters=filters,
                        ),
                        sub_group_by_fields=issue_group_values(
                            field=sub_group_by,
                            slug=slug,
                            project_id=project_id,
                            filters=filters,
                        ),
                        group_by_field_name=group_by,
                        sub_group_by_field_name=sub_group_by,
                        count_filter=Q(
                            Q(issue_intake__status=1)
                            | Q(issue_intake__status=-1)
                            | Q(issue_intake__status=2)
                            | Q(issue_intake__isnull=True),
                            archived_at__isnull=True,
                            is_draft=False,
                        ),
                    )
            else:
                issues = self.paginate(
                    request=request,
                    order_by=order_by_param,
                    queryset=issue_queryset,
                    on_results=lambda issues: issue_on_results(
                        group_by=group_by, issues=issues, sub_group_by=sub_group_by
                    ),
                    paginator_cls=GroupedOffsetPaginator,
                    group_by_fields=issue_group_values(
                        field=group_by,
                        slug=slug,
                        project_id=project_id,
                        filters=filters,
                    ),
                    group_by_field_name=group_by,
                    count_filter=Q(
                        Q(issue_intake__status=1)
                        | Q(issue_intake__status=-1)
                        | Q(issue_intake__status=2)
                        | Q(issue_intake__isnull=True),
                        archived_at__isnull=True,
                        is_draft=False,
                    ),
                )
        else:
            issues = self.paginate(
                order_by=order_by_param,
                request=request,
                queryset=issue_queryset,
                on_results=lambda issues: issue_on_results(group_by=group_by, issues=issues, sub_group_by=sub_group_by),
            )

        return Response(
            {
                "settings": settings_serializer.data,
                "issues": issues,
            },
            status=status.HTTP_200_OK,
        )
