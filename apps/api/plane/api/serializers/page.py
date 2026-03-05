# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from rest_framework import serializers

from plane.db.models import Page, PageLabel
from plane.api.serializers.base import BaseSerializer
from plane.api.serializers.user import UserLiteSerializer


class PageSerializer(BaseSerializer):
    owned_by = UserLiteSerializer(read_only=True)

    class Meta:
        model = Page
        read_only_fields = [
            "id",
            "workspace",
            "created_by",
            "updated_by",
            "owned_by",
            "description_stripped",
            "moved_to_page",
            "moved_to_project",
        ]
        exclude = []


class PageDetailSerializer(BaseSerializer):
    owned_by = UserLiteSerializer(read_only=True)
    labels = serializers.SerializerMethodField()

    class Meta:
        model = Page
        read_only_fields = [
            "id",
            "workspace",
            "created_by",
            "updated_by",
            "owned_by",
            "description_stripped",
            "moved_to_page",
            "moved_to_project",
        ]
        exclude = []

    def get_labels(self, obj):
        return list(obj.labels.values_list("id", flat=True))
