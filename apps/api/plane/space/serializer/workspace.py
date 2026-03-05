# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Module imports
from rest_framework import serializers
from .base import BaseSerializer
from plane.db.models import Workspace, Project, DeployBoard, ProjectMember
from django.db.models import Count, Q


class WorkspaceLiteSerializer(BaseSerializer):
    class Meta:
        model = Workspace
        fields = ["name", "slug", "id"]
        read_only_fields = fields


class WorkspacePublicSerializer(BaseSerializer):
    logo_url = serializers.CharField(read_only=True)

    class Meta:
        model = Workspace
        fields = ["name", "slug", "id", "logo_url", "description"]
        read_only_fields = fields


class PublicProjectSerializer(BaseSerializer):
    member_count = serializers.IntegerField(read_only=True)
    issue_count = serializers.IntegerField(read_only=True)
    anchor = serializers.CharField(read_only=True)
    is_comments_enabled = serializers.BooleanField(read_only=True)
    is_reactions_enabled = serializers.BooleanField(read_only=True)
    is_votes_enabled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "member_count",
            "issue_count",
            "anchor",
            "is_comments_enabled",
            "is_reactions_enabled",
            "is_votes_enabled",
        ]
        read_only_fields = fields
