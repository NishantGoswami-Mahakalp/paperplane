# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from rest_framework import status
from rest_framework.response import Response

from plane.api.views.base import BaseAPIView
from plane.db.models import IssueTemplate, PageTemplate, Issue, Page, Project
from plane.api.serializers import (
    IssueTemplateSerializer,
    IssueTemplateCreateSerializer,
    IssueTemplateDetailSerializer,
    PageTemplateSerializer,
    PageTemplateCreateSerializer,
    PageTemplateDetailSerializer,
    TemplateInstantiateSerializer,
    IssueSerializer,
    PageSerializer,
)
from plane.app.permissions import ProjectEntityPermission, ProjectMemberPermission, ProjectLitePermission


class IssueTemplateListCreateAPIEndpoint(BaseAPIView):
    """Issue Template List and Create Endpoint"""

    model = IssueTemplate
    serializer_class = IssueTemplateSerializer
    permission_classes = [ProjectMemberPermission]

    def get_queryset(self):
        return IssueTemplate.objects.filter(
            workspace__slug=self.kwargs.get("slug"),
            project_id=self.kwargs.get("project_id"),
        ).order_by("-created_at")

    def get(self, request, slug, project_id):
        templates = self.get_queryset()
        serializer = IssueTemplateDetailSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, slug, project_id):
        project = Project.objects.get(pk=project_id)
        serializer = IssueTemplateCreateSerializer(
            data=request.data,
            context={
                "project_id": project_id,
                "workspace_id": project.workspace_id,
            },
        )
        if serializer.is_valid():
            serializer.save(
                workspace_id=project.workspace_id,
                project_id=project_id,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueTemplateDetailAPIEndpoint(BaseAPIView):
    """Issue Template Detail Endpoint"""

    model = IssueTemplate
    serializer_class = IssueTemplateSerializer
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return IssueTemplate.objects.filter(
            workspace__slug=self.kwargs.get("slug"),
            project_id=self.kwargs.get("project_id"),
        )

    def get(self, request, slug, project_id, template_id):
        template = self.get_queryset().get(pk=template_id)
        serializer = IssueTemplateDetailSerializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug, project_id, template_id):
        template = self.get_queryset().get(pk=template_id)
        template.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueTemplateInstantiateAPIEndpoint(BaseAPIView):
    """Instantiate Issue Template API Endpoint"""

    model = IssueTemplate
    permission_classes = [ProjectMemberPermission]

    def post(self, request, slug, project_id, template_id):
        template = IssueTemplate.objects.get(
            workspace__slug=slug,
            project_id=project_id,
            pk=template_id,
        )

        serializer = TemplateInstantiateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        name = data.get("name") or template.name
        target_project_id = data.get("project_id") or project_id

        target_project = Project.objects.get(pk=target_project_id)

        name = self._get_unique_name(target_project, name)

        issue = Issue.objects.create(
            workspace=template.workspace,
            project=target_project,
            name=name,
            description=template.description,
            description_html=template.description_html,
            description_json=template.description_json,
            description_binary=template.description_binary,
            priority=template.priority,
            state=template.state,
            type=template.type,
            start_date=template.start_date,
            target_date=template.target_date,
            estimate_point=template.estimate_point,
        )

        template_labels = template.labels.values_list("id", flat=True)
        if template_labels:
            from plane.db.models import IssueLabel

            IssueLabel.objects.bulk_create(
                [IssueLabel(issue=issue, label_id=label_id) for label_id in template_labels],
                ignore_conflicts=True,
            )

        template_assignees = template.assignees.values_list("id", flat=True)
        if template_assignees:
            from plane.db.models import IssueAssignee

            IssueAssignee.objects.bulk_create(
                [IssueAssignee(issue=issue, assignee_id=assignee_id) for assignee_id in template_assignees],
                ignore_conflicts=True,
            )

        from plane.api.serializers import IssueSerializer

        return Response(
            IssueSerializer(issue).data,
            status=status.HTTP_201_CREATED,
        )

    def _get_unique_name(self, project, name):
        base_name = name
        counter = 1

        while Issue.objects.filter(project=project, name=name).exists():
            counter += 1
            name = f"{base_name} ({counter})"

        return name


class PageTemplateListCreateAPIEndpoint(BaseAPIView):
    """Page Template List and Create Endpoint"""

    model = PageTemplate
    serializer_class = PageTemplateSerializer
    permission_classes = [ProjectMemberPermission]

    def get_queryset(self):
        return PageTemplate.objects.filter(
            workspace__slug=self.kwargs.get("slug"),
            project_id=self.kwargs.get("project_id"),
        ).order_by("-created_at")

    def get(self, request, slug, project_id):
        templates = self.get_queryset()
        serializer = PageTemplateDetailSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, slug, project_id):
        project = Project.objects.get(pk=project_id)
        serializer = PageTemplateCreateSerializer(
            data=request.data,
            context={
                "project_id": project_id,
                "workspace_id": project.workspace_id,
            },
        )
        if serializer.is_valid():
            serializer.save(
                workspace_id=project.workspace_id,
                project_id=project_id,
                owned_by=self.request.user,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PageTemplateDetailAPIEndpoint(BaseAPIView):
    """Page Template Detail Endpoint"""

    model = PageTemplate
    serializer_class = PageTemplateSerializer
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return PageTemplate.objects.filter(
            workspace__slug=self.kwargs.get("slug"),
            project_id=self.kwargs.get("project_id"),
        )

    def get(self, request, slug, project_id, template_id):
        template = self.get_queryset().get(pk=template_id)
        serializer = PageTemplateDetailSerializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug, project_id, template_id):
        template = self.get_queryset().get(pk=template_id)
        template.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PageTemplateInstantiateAPIEndpoint(BaseAPIView):
    """Instantiate Page Template API Endpoint"""

    model = PageTemplate
    permission_classes = [ProjectMemberPermission]

    def post(self, request, slug, project_id, template_id):
        template = PageTemplate.objects.get(
            workspace__slug=slug,
            project_id=project_id,
            pk=template_id,
        )

        serializer = TemplateInstantiateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        name = data.get("name") or template.name
        target_project_id = data.get("project_id") or project_id

        name = self._get_unique_name(template.workspace_id, target_project_id, name)

        page = Page.objects.create(
            workspace=template.workspace,
            owned_by=self.request.user,
            name=name,
            description_json=template.description_json,
            description_html=template.description_html,
            description_binary=template.description_binary,
            description_stripped=template.description_stripped,
            color=template.color,
            access=template.access,
            is_locked=template.is_locked,
            view_props=template.view_props,
            logo_props=template.logo_props,
        )

        if target_project_id:
            from plane.db.models import ProjectPage

            ProjectPage.objects.create(project_id=target_project_id, page=page)

        template_labels = template.labels.values_list("id", flat=True)
        if template_labels:
            from plane.db.models import PageLabel

            PageLabel.objects.bulk_create(
                [PageLabel(page=page, label_id=label_id) for label_id in template_labels],
                ignore_conflicts=True,
            )

        return Response(
            PageSerializer(page).data,
            status=status.HTTP_201_CREATED,
        )

    def _get_unique_name(self, workspace_id, project_id, name):
        base_name = name
        counter = 1

        query = Page.objects.filter(workspace_id=workspace_id, name=name)
        if project_id:
            query = query.filter(projects__id=project_id)

        while query.exists():
            counter += 1
            name = f"{base_name} ({counter})"
            query = Page.objects.filter(workspace_id=workspace_id, name=name)
            if project_id:
                query = query.filter(projects__id=project_id)

        return name
