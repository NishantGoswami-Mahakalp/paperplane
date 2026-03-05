# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from rest_framework import serializers

from plane.db.models import IssueTemplate, PageTemplate
from plane.api.serializers.base import BaseSerializer
from plane.api.serializers.user import UserLiteSerializer
from plane.api.serializers.state import StateLiteSerializer


class IssueTemplateSerializer(BaseSerializer):
    class Meta:
        model = IssueTemplate
        read_only_fields = ["id", "workspace", "project", "created_by", "updated_by"]
        exclude = []


class IssueTemplateCreateSerializer(BaseSerializer):
    name = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    description_html = serializers.CharField(required=False, default="<p></p>", allow_blank=True)
    description_json = serializers.JSONField(required=False, default=dict)
    priority = serializers.ChoiceField(
        choices=IssueTemplate.PRIORITY_CHOICES,
        required=False,
        default="none",
    )
    state_id = serializers.UUIDField(required=False, allow_null=True)
    type_id = serializers.UUIDField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    target_date = serializers.DateField(required=False, allow_null=True)
    estimate_point_id = serializers.UUIDField(required=False, allow_null=True)
    labels = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )
    assignees = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )
    project_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = IssueTemplate
        read_only_fields = ["id", "workspace", "created_by", "updated_by"]

    def create(self, validated_data):
        labels = validated_data.pop("labels", [])
        assignees = validated_data.pop("assignees", [])

        template = IssueTemplate.objects.create(**validated_data)

        if labels:
            from plane.db.models import IssueTemplateLabel, Label

            label_ids = Label.objects.filter(
                project_id=validated_data.get("project_id"),
                id__in=labels,
            ).values_list("id", flat=True)
            IssueTemplateLabel.objects.bulk_create(
                [IssueTemplateLabel(template=template, label_id=label_id) for label_id in label_ids],
                ignore_conflicts=True,
            )

        if assignees:
            from plane.db.models import IssueTemplateAssignee

            IssueTemplateAssignee.objects.bulk_create(
                [IssueTemplateAssignee(template=template, assignee_id=assignee_id) for assignee_id in assignees],
                ignore_conflicts=True,
            )

        return template


class IssueTemplateDetailSerializer(BaseSerializer):
    labels = serializers.SerializerMethodField()
    assignees = serializers.SerializerMethodField()

    class Meta:
        model = IssueTemplate
        read_only_fields = ["id", "workspace", "project", "created_by", "updated_by"]

    def get_labels(self, obj):
        return list(obj.labels.values_list("id", flat=True))

    def get_assignees(self, obj):
        return list(obj.assignees.values_list("id", flat=True))


class PageTemplateSerializer(BaseSerializer):
    class Meta:
        model = PageTemplate
        read_only_fields = ["id", "workspace", "project", "created_by", "updated_by"]
        exclude = []


class PageTemplateCreateSerializer(BaseSerializer):
    name = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    description_html = serializers.CharField(required=False, default="<p></p>", allow_blank=True)
    description_json = serializers.JSONField(required=False, default=dict)
    color = serializers.CharField(required=False, default="", max_length=255, allow_blank=True)
    access = serializers.ChoiceField(
        choices=PageTemplate.ACCESS_CHOICES,
        required=False,
        default=PageTemplate.PRIVATE_ACCESS,
    )
    is_locked = serializers.BooleanField(required=False, default=False)
    view_props = serializers.JSONField(required=False, default=dict)
    logo_props = serializers.JSONField(required=False, default=dict)
    labels = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )
    project_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = PageTemplate
        read_only_fields = ["id", "workspace", "created_by", "updated_by"]

    def create(self, validated_data):
        labels = validated_data.pop("labels", [])

        template = PageTemplate.objects.create(**validated_data)

        if labels:
            from plane.db.models import PageTemplateLabel, Label

            label_ids = Label.objects.filter(
                project_id=validated_data.get("project_id"),
                id__in=labels,
            ).values_list("id", flat=True)
            PageTemplateLabel.objects.bulk_create(
                [PageTemplateLabel(template=template, label_id=label_id) for label_id in label_ids],
                ignore_conflicts=True,
            )

        return template


class PageTemplateDetailSerializer(BaseSerializer):
    labels = serializers.SerializerMethodField()

    class Meta:
        model = PageTemplate
        read_only_fields = ["id", "workspace", "project", "created_by", "updated_by"]

    def get_labels(self, obj):
        return list(obj.labels.values_list("id", flat=True))


class TemplateInstantiateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    project_id = serializers.UUIDField(required=False, allow_null=True)
