# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.app.views.base import BaseAPIView, BaseViewSet
from plane.app.permissions import WorkspaceUserPermission, WorkSpaceAdminPermission
from plane.app.serializers import (
    TeamspaceSerializer,
    TeamspaceMemberSerializer,
    TeamspaceProjectSerializer,
)
from plane.db.models import Team, TeamspaceMember, TeamspaceProject, Workspace


class TeamspaceViewSet(BaseViewSet):
    model = Team
    serializer_class = TeamspaceSerializer
    permission_classes = [WorkspaceUserPermission]

    def get_queryset(self):
        return super().get_queryset().filter(workspace__slug=self.kwargs.get("slug"))

    def create(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        serializer = TeamspaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(workspace=workspace)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, slug):
        queryset = self.get_queryset()
        serializer = TeamspaceSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, slug, pk):
        teamspace = self.get_object()
        serializer = TeamspaceSerializer(teamspace)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, slug, pk):
        teamspace = self.get_object()
        serializer = TeamspaceSerializer(teamspace, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, slug, pk):
        teamspace = self.get_object()
        teamspace.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamspaceMemberViewSet(BaseViewSet):
    model = TeamspaceMember
    serializer_class = TeamspaceMemberSerializer
    permission_classes = [WorkspaceUserPermission]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(team__workspace__slug=self.kwargs.get("slug"), team_id=self.kwargs.get("teamspace_id"))
        )

    def create(self, request, slug, teamspace_id):
        serializer = TeamspaceMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(team_id=teamspace_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, slug, teamspace_id):
        queryset = self.get_queryset()
        serializer = TeamspaceMemberSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, slug, teamspace_id, pk):
        member = self.get_object()
        serializer = TeamspaceMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, slug, teamspace_id, pk):
        member = self.get_object()
        serializer = TeamspaceMemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, slug, teamspace_id, pk):
        member = self.get_object()
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamspaceProjectViewSet(BaseViewSet):
    model = TeamspaceProject
    serializer_class = TeamspaceProjectSerializer
    permission_classes = [WorkspaceUserPermission]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(team__workspace__slug=self.kwargs.get("slug"), team_id=self.kwargs.get("teamspace_id"))
            .select_related("project")
        )

    def create(self, request, slug, teamspace_id):
        serializer = TeamspaceProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(team_id=teamspace_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, slug, teamspace_id):
        queryset = self.get_queryset()
        serializer = TeamspaceProjectSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug, teamspace_id, pk):
        project_link = self.get_object()
        project_link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamspaceProjectsByProjectAPIEndpoint(BaseAPIView):
    permission_classes = [WorkspaceUserPermission]

    def get(self, request, slug, project_id):
        teamspace_projects = TeamspaceProject.objects.filter(
            team__workspace__slug=slug, project_id=project_id
        ).select_related("team")
        serializer = TeamspaceProjectSerializer(teamspace_projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
