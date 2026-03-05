# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Third party imports
from rest_framework import serializers

# Module imports
from plane.db.models import (
    WorkItemType,
    ProjectWorkItemType,
    FieldDefinition,
    WorkItemTypeField,
    get_default_work_item_fields,
)
from .base import BaseSerializer


class FieldDefinitionSerializer(BaseSerializer):
    class Meta:
        model = FieldDefinition
        read_only_fields = ["id", "workspace", "created_by", "updated_by", "created_at", "updated_at"]
        exclude = []


class FieldDefinitionLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldDefinition
        fields = ["id", "name", "description", "field_type", "is_required", "position", "validation_rules", "options"]
        read_only_fields = fields


class WorkItemTypeFieldSerializer(BaseSerializer):
    field_definition = FieldDefinitionLiteSerializer(read_only=True)
    field_definition_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldDefinition.objects.all(), source="field_definition", write_only=True
    )

    class Meta:
        model = WorkItemTypeField
        read_only_fields = ["id", "work_item_type", "created_by", "updated_by", "created_at", "updated_at"]
        exclude = []


class WorkItemTypeFieldCreateSerializer(BaseSerializer):
    field_definition_id = serializers.PrimaryKeyRelatedField(queryset=FieldDefinition.objects.all())
    is_required = serializers.BooleanField(required=False, default=False)
    position = serializers.IntegerField(required=False, default=0)
    validations = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = WorkItemTypeField
        read_only_fields = ["id", "work_item_type", "created_by", "updated_by", "created_at", "updated_at"]
        exclude = []


class WorkItemTypeSerializer(BaseSerializer):
    work_item_type_fields = WorkItemTypeFieldSerializer(many=True, read_only=True)

    class Meta:
        model = WorkItemType
        read_only_fields = [
            "id",
            "workspace",
            "schema_version",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        exclude = []


class WorkItemTypeLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItemType
        fields = [
            "id",
            "name",
            "description",
            "work_item_type",
            "logo_props",
            "is_epic",
            "is_default",
            "is_active",
            "schema_version",
        ]
        read_only_fields = fields


class WorkItemTypeCreateSerializer(BaseSerializer):
    default_fields = serializers.JSONField(required=False, default=None)

    class Meta:
        model = WorkItemType
        read_only_fields = [
            "id",
            "workspace",
            "schema_version",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        exclude = []


class ProjectWorkItemTypeSerializer(BaseSerializer):
    work_item_type = WorkItemTypeLiteSerializer(read_only=True)
    work_item_type_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkItemType.objects.all(), source="work_item_type", write_only=True
    )

    class Meta:
        model = ProjectWorkItemType
        read_only_fields = ["id", "project", "workspace", "created_by", "updated_by", "created_at", "updated_at"]
        exclude = []


class ProjectWorkItemTypeCreateSerializer(BaseSerializer):
    work_item_type_id = serializers.PrimaryKeyRelatedField(queryset=WorkItemType.objects.all())
    position = serializers.IntegerField(required=False, default=0)
    is_default = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = ProjectWorkItemType
        read_only_fields = ["id", "project", "workspace", "created_by", "updated_by", "created_at", "updated_at"]
        exclude = []
