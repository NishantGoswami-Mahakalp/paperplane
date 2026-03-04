# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import requests

# Django imports
from django.conf import settings

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.app.permissions import ROLE, allow_permission
from plane.app.serializers import ProjectLiteSerializer
from plane.app.views.base import BaseAPIView
from plane.db.models import Project, Workspace, WorkspaceIntegration, ForgejoRepository, ForgejoRepositorySync


class ForgejoRepositoriesEndpoint(BaseAPIView):
    @allow_permission(allowed_roles=[ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def get(self, request, slug, integration_id):
        workspace_integration = WorkspaceIntegration.objects.get(
            workspace__slug=slug,
            id=integration_id,
        )

        api_token = workspace_integration.api_token.token
        base_url = workspace_integration.config.get("forgejo_url")
        if not base_url:
            return Response(
                {"error": "Forgejo URL not configured"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = {
            "Authorization": f"token {api_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(
                f"{base_url}/api/v1/user/repos",
                headers=headers,
                params={"limit": 100},
            )
            response.raise_for_status()
            repositories = response.json()
        except requests.RequestException as e:
            return Response(
                {"error": f"Failed to fetch repositories: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            [
                {
                    "id": repo.get("id"),
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "url": repo.get("html_url"),
                    "description": repo.get("description"),
                    "private": repo.get("private"),
                }
                for repo in repositories
            ],
            status=status.HTTP_200_OK,
        )


class ForgejoImporterInfoEndpoint(BaseAPIView):
    @allow_permission(allowed_roles=[ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def get(self, request, slug):
        repository_full_name = request.GET.get("repository", None)
        workspace_integration_id = request.GET.get("integration_id", None)

        if not repository_full_name or not workspace_integration_id:
            return Response(
                {"error": "repository and integration_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            workspace_integration = WorkspaceIntegration.objects.get(
                workspace__slug=slug,
                id=workspace_integration_id,
            )
        except WorkspaceIntegration.DoesNotExist:
            return Response(
                {"error": "Workspace integration not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        api_token = workspace_integration.api_token.token
        base_url = workspace_integration.config.get("forgejo_url")
        if not base_url:
            return Response(
                {"error": "Forgejo URL not configured"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = {
            "Authorization": f"token {api_token}",
            "Content-Type": "application/json",
        }

        try:
            repo_response = requests.get(
                f"{base_url}/api/v1/repos/{repository_full_name}",
                headers=headers,
            )
            repo_response.raise_for_status()
            repo_info = repo_response.json()

            issues_response = requests.get(
                f"{base_url}/api/v1/repos/{repository_full_name}/issues",
                headers=headers,
                params={"state": "all", "limit": 100},
            )
            issues_response.raise_for_status()
            issues = issues_response.json()

            labels_response = requests.get(
                f"{base_url}/api/v1/repos/{repository_full_name}/labels",
                headers=headers,
            )
            labels_response.raise_for_status()
            labels = labels_response.json()

            collaborators_response = requests.get(
                f"{base_url}/api/v1/repos/{repository_full_name}/collaborators",
                headers=headers,
            )
            collaborators_response.raise_for_status()
            collaborators = collaborators_response.json()

        except requests.RequestException as e:
            return Response(
                {"error": f"Failed to fetch repository info: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "repository": {
                    "id": repo_info.get("id"),
                    "name": repo_info.get("name"),
                    "full_name": repo_info.get("full_name"),
                    "url": repo_info.get("html_url"),
                    "description": repo_info.get("description"),
                    "private": repo_info.get("private"),
                    "open_issues_count": repo_info.get("open_issues_count"),
                },
                "issues": [
                    {
                        "id": issue.get("id"),
                        "number": issue.get("number"),
                        "title": issue.get("title"),
                        "body": issue.get("body"),
                        "state": issue.get("state"),
                        "labels": [
                            {"name": label.get("name"), "color": label.get("color")}
                            for label in issue.get("labels", [])
                        ],
                        "assignee": (
                            {
                                "id": issue.get("assignee", {}).get("id"),
                                "login": issue.get("assignee", {}).get("login"),
                            }
                            if issue.get("assignee")
                            else None
                        ),
                    }
                    for issue in issues
                ],
                "labels": [
                    {"id": label.get("id"), "name": label.get("name"), "color": label.get("color")} for label in labels
                ],
                "collaborators": [
                    {
                        "id": collab.get("id"),
                        "login": collab.get("login"),
                        "email": collab.get("email"),
                    }
                    for collab in collaborators
                ],
            },
            status=status.HTTP_200_OK,
        )


class ForgejoImporterCreateEndpoint(BaseAPIView):
    @allow_permission(allowed_roles=[ROLE.ADMIN], level="WORKSPACE")
    def post(self, request, slug, project_id):
        repository_id = request.data.get("repository_id")
        repository_full_name = request.data.get("repository_full_name")
        workspace_integration_id = request.data.get("workspace_integration_id")
        import_issues = request.data.get("import_issues", True)
        import_labels = request.data.get("import_labels", True)

        if not repository_id or not repository_full_name or not workspace_integration_id:
            return Response(
                {"error": "repository_id, repository_full_name, and workspace_integration_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(pk=project_id, workspace__slug=slug)
            workspace = Workspace.objects.get(slug=slug)
            workspace_integration = WorkspaceIntegration.objects.get(
                workspace=workspace,
                id=workspace_integration_id,
            )
        except (Project.DoesNotExist, Workspace.DoesNotExist, WorkspaceIntegration.DoesNotExist) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

        api_token = workspace_integration.api_token.token
        base_url = workspace_integration.config.get("forgejo_url")

        if not base_url:
            return Response(
                {"error": "Forgejo URL not configured"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = {
            "Authorization": f"token {api_token}",
            "Content-Type": "application/json",
        }

        try:
            repo_response = requests.get(
                f"{base_url}/api/v1/repos/{repository_full_name}",
                headers=headers,
            )
            repo_response.raise_for_status()
            repo_info = repo_response.json()
        except requests.RequestException as e:
            return Response(
                {"error": f"Failed to fetch repository: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        forgejo_repository = ForgejoRepository.objects.create(
            name=repo_info.get("name"),
            url=repo_info.get("html_url"),
            repository_id=repository_id,
            owner=repo_info.get("owner", {}).get("login", ""),
            config={
                "forgejo_url": base_url,
                "repository_full_name": repository_full_name,
            },
            project=project,
            workspace=workspace,
        )

        forgejo_sync = ForgejoRepositorySync.objects.create(
            repository=forgejo_repository,
            credentials={"api_token": api_token},
            actor=request.user,
            workspace_integration=workspace_integration,
            project=project,
            workspace=workspace,
        )

        return Response(
            {
                "id": str(forgejo_repository.id),
                "name": forgejo_repository.name,
                "url": forgejo_repository.url,
                "repository_id": forgejo_repository.repository_id,
                "sync_id": str(forgejo_sync.id),
                "import_issues": import_issues,
                "import_labels": import_labels,
            },
            status=status.HTTP_201_CREATED,
        )


class ForgejoRepositorySyncEndpoint(BaseAPIView):
    @allow_permission(allowed_roles=[ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def post(self, request, slug, project_id, sync_id):
        try:
            sync = ForgejoRepositorySync.objects.get(
                id=sync_id,
                project__workspace__slug=slug,
                project_id=project_id,
            )
        except ForgejoRepositorySync.DoesNotExist:
            return Response(
                {"error": "Repository sync not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        headers = {
            "Authorization": f"token {sync.credentials.get('api_token')}",
            "Content-Type": "application/json",
        }

        base_url = sync.repository.config.get("forgejo_url")
        repo_full_name = sync.repository.config.get("repository_full_name")

        try:
            issues_response = requests.get(
                f"{base_url}/api/v1/repos/{repo_full_name}/issues",
                headers=headers,
                params={"state": "all", "limit": 100},
            )
            issues_response.raise_for_status()
            issues = issues_response.json()
        except requests.RequestException as e:
            return Response(
                {"error": f"Failed to fetch issues: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "sync_id": str(sync.id),
                "repository_name": sync.repository.name,
                "issues_count": len(issues),
                "last_synced_at": sync.updated_at,
            },
            status=status.HTTP_200_OK,
        )

    @allow_permission(allowed_roles=[ROLE.ADMIN], level="WORKSPACE")
    def patch(self, request, slug, project_id, sync_id):
        try:
            sync = ForgejoRepositorySync.objects.get(
                id=sync_id,
                project__workspace__slug=slug,
                project_id=project_id,
            )
        except ForgejoRepositorySync.DoesNotExist:
            return Response(
                {"error": "Repository sync not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        label_id = request.data.get("label_id")
        if label_id:
            from plane.db.models import Label

            try:
                label = Label.objects.get(pk=label_id, project_id=project_id)
                sync.label = label
                sync.save()
            except Label.DoesNotExist:
                return Response(
                    {"error": "Label not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(
            {
                "id": str(sync.id),
                "repository_name": sync.repository.name,
                "label": ({"id": str(sync.label.id), "name": sync.label.name} if sync.label else None),
            },
            status=status.HTTP_200_OK,
        )

    @allow_permission(allowed_roles=[ROLE.ADMIN], level="WORKSPACE")
    def delete(self, request, slug, project_id, sync_id):
        try:
            sync = ForgejoRepositorySync.objects.get(
                id=sync_id,
                project__workspace__slug=slug,
                project_id=project_id,
            )
        except ForgejoRepositorySync.DoesNotExist:
            return Response(
                {"error": "Repository sync not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        sync.repository.delete()
        sync.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class ForgejoRepositorySyncListEndpoint(BaseAPIView):
    @allow_permission(allowed_roles=[ROLE.ADMIN, ROLE.MEMBER], level="WORKSPACE")
    def get(self, request, slug, project_id):
        syncs = ForgejoRepositorySync.objects.filter(
            project__workspace__slug=slug,
            project_id=project_id,
        ).select_related("repository", "label", "workspace_integration")

        return Response(
            [
                {
                    "id": str(sync.id),
                    "repository": {
                        "id": str(sync.repository.id),
                        "name": sync.repository.name,
                        "url": sync.repository.url,
                        "repository_id": sync.repository.repository_id,
                    },
                    "label": ({"id": str(sync.label.id), "name": sync.label.name} if sync.label else None),
                    "created_at": sync.created_at,
                    "updated_at": sync.updated_at,
                }
                for sync in syncs
            ],
            status=status.HTTP_200_OK,
        )
