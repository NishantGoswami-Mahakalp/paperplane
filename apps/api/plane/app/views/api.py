# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python import
from uuid import uuid4
from typing import Optional

# Django import
from django.contrib.auth.hashers import make_password

# Third party
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

# Module import
from .base import BaseAPIView
from plane.db.models import APIToken, Project, ProjectMember, User, Workspace, WorkspaceMember
from plane.app.serializers import APITokenSerializer, APITokenReadSerializer
from plane.app.permissions import WorkspaceOwnerPermission

SEVA_SERVICE_BOT_TYPE = "SEVA_SERVICE"


def _normalize_allowed_project_ids(workspace: Workspace, allowed_project_ids):
    if allowed_project_ids is None:
        return None

    if not isinstance(allowed_project_ids, list):
        raise ValueError("allowed_project_ids must be a list")

    normalized_project_ids = [str(project_id) for project_id in allowed_project_ids]
    if not normalized_project_ids:
        return []

    project_count = Project.objects.filter(workspace=workspace, pk__in=normalized_project_ids).count()
    if project_count != len(set(normalized_project_ids)):
        raise ValueError("allowed_project_ids must reference projects in the workspace")

    return normalized_project_ids


def _get_or_create_service_user(workspace: Workspace) -> User:
    identity_suffix = workspace.id.hex
    bot_user, _ = User.objects.get_or_create(
        email=f"seva-bot+{identity_suffix}@plane.so",
        defaults={
            "username": f"seva_bot_{identity_suffix}",
            "display_name": "Seva",
            "first_name": "Seva",
            "last_name": "Bot",
            "is_bot": True,
            "bot_type": SEVA_SERVICE_BOT_TYPE,
            "password": make_password(uuid4().hex),
            "is_password_autoset": True,
            "is_active": True,
        },
    )

    fields_to_update = []
    if not bot_user.is_bot:
        bot_user.is_bot = True
        fields_to_update.append("is_bot")
    if bot_user.bot_type != SEVA_SERVICE_BOT_TYPE:
        bot_user.bot_type = SEVA_SERVICE_BOT_TYPE
        fields_to_update.append("bot_type")
    if not bot_user.is_active:
        bot_user.is_active = True
        fields_to_update.append("is_active")
    if fields_to_update:
        bot_user.save(update_fields=fields_to_update)

    WorkspaceMember.objects.update_or_create(
        workspace=workspace,
        member=bot_user,
        defaults={
            "role": 20,
            "company_role": "",
            "is_active": True,
        },
    )

    return bot_user


def _sync_service_user_project_memberships(workspace: Workspace, service_user: User, allowed_project_ids) -> None:
    scoped_projects = Project.objects.filter(workspace=workspace)
    if allowed_project_ids:
        scoped_projects = scoped_projects.filter(pk__in=allowed_project_ids)

    desired_project_ids = set(str(project.id) for project in scoped_projects.only("id"))

    ProjectMember.objects.filter(
        project__workspace=workspace,
        member=service_user,
        deleted_at__isnull=True,
    ).exclude(project_id__in=desired_project_ids).update(is_active=False)

    for project in scoped_projects:
        ProjectMember.objects.update_or_create(
            project=project,
            member=service_user,
            defaults={
                "role": 20,
                "is_active": True,
            },
        )


class ApiTokenEndpoint(BaseAPIView):
    def post(self, request: Request) -> Response:
        label = request.data.get("label", str(uuid4().hex))
        description = request.data.get("description", "")
        expired_at = request.data.get("expired_at", None)

        # Check the user type
        user_type = 1 if request.user.is_bot else 0

        api_token = APIToken.objects.create(
            label=label,
            description=description,
            user=request.user,
            user_type=user_type,
            expired_at=expired_at,
        )

        serializer = APITokenSerializer(api_token)
        # Token will be only visible while creating
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request: Request, pk: Optional[str] = None) -> Response:
        if pk is None:
            api_tokens = APIToken.objects.filter(user=request.user, is_service=False)
            serializer = APITokenReadSerializer(api_tokens, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            api_tokens = APIToken.objects.get(user=request.user, pk=pk, is_service=False)
            serializer = APITokenReadSerializer(api_tokens)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk: str) -> Response:
        api_token = APIToken.objects.get(user=request.user, pk=pk, is_service=False)
        api_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request: Request, pk: str) -> Response:
        api_token = APIToken.objects.get(user=request.user, pk=pk, is_service=False)
        serializer = APITokenSerializer(api_token, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceApiTokenEndpoint(BaseAPIView):
    permission_classes = [WorkspaceOwnerPermission]

    def post(self, request: Request, slug: str) -> Response:
        workspace = Workspace.objects.get(slug=slug)
        service_user = _get_or_create_service_user(workspace)
        try:
            allowed_project_ids = _normalize_allowed_project_ids(workspace, request.data.get("allowed_project_ids"))
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        api_token = APIToken.objects.filter(workspace=workspace, is_service=True).first()
        effective_allowed_project_ids = allowed_project_ids if allowed_project_ids is not None else []

        if api_token:
            effective_allowed_project_ids = api_token.allowed_project_ids
            if allowed_project_ids is not None:
                api_token.allowed_project_ids = allowed_project_ids
                effective_allowed_project_ids = allowed_project_ids

            update_fields = []
            if api_token.user_id != service_user.id:
                api_token.user = service_user
                update_fields.append("user")
            if api_token.user_type != 1:
                api_token.user_type = 1
                update_fields.append("user_type")
            if allowed_project_ids is not None:
                update_fields.append("allowed_project_ids")
            if update_fields:
                api_token.save(update_fields=update_fields)

            _sync_service_user_project_memberships(workspace, service_user, effective_allowed_project_ids)

            return Response(
                {
                    "created": False,
                    "allowed_project_ids": api_token.allowed_project_ids,
                },
                status=status.HTTP_200_OK,
            )
        else:
            _sync_service_user_project_memberships(workspace, service_user, effective_allowed_project_ids)

            api_token = APIToken.objects.create(
                label=str(uuid4().hex),
                description="Service Token",
                user=service_user,
                workspace=workspace,
                user_type=1,
                is_service=True,
                allowed_project_ids=allowed_project_ids or [],
            )
            return Response(
                {
                    "created": True,
                    "token": str(api_token.token),
                    "allowed_project_ids": api_token.allowed_project_ids,
                },
                status=status.HTTP_201_CREATED,
            )
