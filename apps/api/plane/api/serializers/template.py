# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from rest_framework import serializers

from plane.db.models import IssueTemplate, PageTemplate, Template, TemplateField, TemplateVersion
from plane.api.serializers.base import BaseSerializer
from plane.api.serializers.user import UserLiteSerializer
from plane.api.serializers.state import StateLiteSerializer


# Lazy import to avoid Django app not ready error
def get_template_type_choices():
    from plane.db.models.template import TemplateType

    return TemplateType.CHOICES


def get_issue_template_priority_choices():
    from plane.db.models.template import IssueTemplate

    return IssueTemplate.PRIORITY_CHOICES


def get_page_template_access_choices():
    from plane.db.models.page import Page

    return Page.ACCESS_CHOICES


def get_page_template_default_access():
    from plane.db.models.page import Page

    return Page.PRIVATE_ACCESS


class TemplateFieldSerializer(BaseSerializer):
    class Meta:
        model = TemplateField
        read_only_fields = ["id", "created_by", "updated_by"]
        exclude = []


class TemplateFieldCreateSerializer(BaseSerializer):
    name = serializers.CharField(required=True, max_length=255)
    field_type = serializers.ChoiceField(choices=TemplateField.FIELD_TYPES)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    default_value = serializers.JSONField(required=False, default=dict)
    options = serializers.ListField(required=False, default=list)
    is_required = serializers.BooleanField(required=False, default=False)
    sort_order = serializers.IntegerField(required=False, default=0)

    class Meta:
        model = TemplateField
        read_only_fields = ["id", "created_by", "updated_by"]


class TemplateVersionSerializer(BaseSerializer):
    class Meta:
        model = TemplateVersion
        read_only_fields = ["id", "created_by", "updated_by"]
        exclude = []


class TemplateSerializer(BaseSerializer):
    fields = TemplateFieldSerializer(many=True, read_only=True)
    current_version = serializers.SerializerMethodField()

    class Meta:
        model = Template
        read_only_fields = ["id", "workspace", "project", "created_by", "updated_by"]
        exclude = []

    def get_current_version(self, obj):
        latest = obj.versions.first()
        return latest.version if latest else None


class TemplateCreateSerializer(BaseSerializer):
    name = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    entity_type = serializers.ChoiceField(choices=get_template_type_choices(), default="work_item")
    schema_version = serializers.IntegerField(required=False, default=1)
    is_active = serializers.BooleanField(required=False, default=True)
    project_id = serializers.UUIDField(required=False, allow_null=True)
    fields = TemplateFieldCreateSerializer(many=True, required=False, default=list)

    class Meta:
        model = Template
        read_only_fields = ["id", "workspace", "created_by", "updated_by"]

    def create(self, validated_data):
        fields_data = validated_data.pop("fields", [])
        workspace_id = validated_data.get("workspace_id")

        template = Template.objects.create(
            workspace_id=workspace_id,
            **validated_data,
        )

        for idx, field_data in enumerate(fields_data):
            field_data["sort_order"] = field_data.get("sort_order", idx)
            TemplateField.objects.create(template=template, **field_data)

        if fields_data:
            TemplateVersion.create_version(template, "Initial version")

        return template

    def update(self, instance, validated_data):
        fields_data = validated_data.pop("fields", None)
        create_version = validated_data.pop("create_version", False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if fields_data is not None:
            existing_fields = {f.id: f for f in instance.fields.all()}
            incoming_field_ids = set()

            for idx, field_data in enumerate(fields_data):
                field_id = field_data.get("id")
                field_data["sort_order"] = field_data.get("sort_order", idx)

                if field_id and str(field_id) in existing_fields:
                    field = existing_fields.pop(str(field_id))
                    for attr, value in field_data.items():
                        setattr(field, attr, value)
                    field.save()
                    incoming_field_ids.add(field.id)
                else:
                    new_field = TemplateField.objects.create(template=instance, **field_data)
                    incoming_field_ids.add(new_field.id)

            for field in existing_fields.values():
                field.delete()

        if create_version or fields_data is not None:
            TemplateVersion.create_version(instance, validated_data.get("change_summary", ""))

        return instance


class TemplateDetailSerializer(BaseSerializer):
    fields = TemplateFieldSerializer(many=True)
    versions = TemplateVersionSerializer(many=True, read_only=True)
    current_version = serializers.SerializerMethodField()

    class Meta:
        model = Template
        read_only_fields = ["id", "workspace", "project", "created_by", "updated_by"]

    def get_current_version(self, obj):
        latest = obj.versions.first()
        return TemplateVersionSerializer(latest).data if latest else None


class TemplateExportSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    entity_type = serializers.CharField()
    schema_version = serializers.IntegerField()
    fields = TemplateFieldSerializer(many=True)
    exported_at = serializers.DateTimeField(read_only=True)


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
        choices=get_issue_template_priority_choices(),
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
        choices=get_page_template_access_choices(),
        required=False,
        default=get_page_template_default_access(),
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
