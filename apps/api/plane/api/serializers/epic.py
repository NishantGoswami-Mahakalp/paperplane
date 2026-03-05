# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Third party imports
from rest_framework import serializers

# Module imports
from .base import BaseSerializer
from plane.db.models import (
    User,
    Epic,
    EpicIssue,
    EpicLink,
    EpicMember,
    Initiative,
    InitiativeEpic,
    InitiativeLink,
    InitiativeMember,
    ProjectMember,
    Project,
)


class InitiativeCreateSerializer(BaseSerializer):
    """
    Serializer for creating initiatives with member validation and date checking.
    """

    members = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Initiative
        fields = [
            "name",
            "description",
            "start_date",
            "target_date",
            "status",
            "lead",
            "members",
            "external_source",
            "external_id",
        ]
        read_only_fields = [
            "id",
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "deleted_at",
        ]

    def validate(self, data):
        project_id = self.context.get("project_id")
        if not project_id:
            raise serializers.ValidationError("Project ID is required")
        project = Project.objects.get(id=project_id)
        if not project:
            raise serializers.ValidationError("Project not found")
        if (
            data.get("start_date", None) is not None
            and data.get("target_date", None) is not None
            and data.get("start_date", None) > data.get("target_date", None)
        ):
            raise serializers.ValidationError("Start date cannot exceed target date")

        if data.get("members", []):
            data["members"] = ProjectMember.objects.filter(
                project_id=self.context.get("project_id"), member_id__in=data["members"]
            ).values_list("member_id", flat=True)

        return data

    def create(self, validated_data):
        members = validated_data.pop("members", None)

        project_id = self.context["project_id"]
        workspace_id = self.context["workspace_id"]

        initiative_name = validated_data.get("name")
        if initiative_name:
            initiative = Initiative.objects.filter(name=initiative_name, project_id=project_id).first()
            if initiative:
                raise serializers.ValidationError(
                    {
                        "id": str(initiative.id),
                        "code": "INITIATIVE_NAME_ALREADY_EXISTS",
                        "error": "Initiative with this name already exists",
                        "message": "Initiative with this name already exists",
                    }
                )

        initiative = Initiative.objects.create(**validated_data, project_id=project_id)
        if members is not None:
            InitiativeMember.objects.bulk_create(
                [
                    InitiativeMember(
                        initiative=initiative,
                        member_id=str(member),
                        project_id=project_id,
                        workspace_id=workspace_id,
                        created_by=initiative.created_by,
                        updated_by=initiative.updated_by,
                    )
                    for member in members
                ],
                batch_size=10,
                ignore_conflicts=True,
            )

        return initiative


class InitiativeUpdateSerializer(InitiativeCreateSerializer):
    """
    Serializer for updating initiatives.
    """

    class Meta(InitiativeCreateSerializer.Meta):
        model = Initiative
        fields = InitiativeCreateSerializer.Meta.fields + [
            "members",
        ]
        read_only_fields = InitiativeCreateSerializer.Meta.read_only_fields

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        initiative_name = validated_data.get("name")
        if initiative_name:
            if (
                Initiative.objects.filter(name=initiative_name, project=instance.project)
                .exclude(id=instance.id)
                .exists()
            ):
                raise serializers.ValidationError({"error": "Initiative with this name already exists"})

        if members is not None:
            InitiativeMember.objects.filter(initiative=instance).delete()
            InitiativeMember.objects.bulk_create(
                [
                    InitiativeMember(
                        initiative=instance,
                        member_id=str(member),
                        project=instance.project,
                        workspace=instance.project.workspace,
                        created_by=instance.created_by,
                        updated_by=instance.updated_by,
                    )
                    for member in members
                ],
                batch_size=10,
                ignore_conflicts=True,
            )

        return super().update(instance, validated_data)


class InitiativeSerializer(BaseSerializer):
    """
    Comprehensive initiative serializer with epic metrics and member management.
    """

    members = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        required=False,
    )
    total_epics = serializers.IntegerField(read_only=True)
    completed_epics = serializers.IntegerField(read_only=True)
    backlog_epics = serializers.IntegerField(read_only=True)
    started_epics = serializers.IntegerField(read_only=True)
    cancelled_epics = serializers.IntegerField(read_only=True)
    total_issues = serializers.IntegerField(read_only=True)
    completed_issues = serializers.IntegerField(read_only=True)

    class Meta:
        model = Initiative
        fields = "__all__"
        read_only_fields = [
            "id",
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "deleted_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["members"] = [str(member.id) for member in instance.members.all()]
        return data


class InitiativeLiteSerializer(BaseSerializer):
    """
    Lightweight initiative serializer for minimal data transfer.
    """

    class Meta:
        model = Initiative
        fields = "__all__"


class InitiativeEpicSerializer(BaseSerializer):
    """
    Serializer for initiative-epic relationships.
    """

    class Meta:
        model = InitiativeEpic
        fields = "__all__"
        read_only_fields = [
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "initiative",
        ]


class InitiativeLinkSerializer(BaseSerializer):
    """
    Serializer for initiative external links.
    """

    class Meta:
        model = InitiativeLink
        fields = "__all__"
        read_only_fields = [
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "initiative",
        ]

    def create(self, validated_data):
        if InitiativeLink.objects.filter(
            url=validated_data.get("url"), initiative_id=validated_data.get("initiative_id")
        ).exists():
            raise serializers.ValidationError({"error": "URL already exists for this Initiative"})
        return InitiativeLink.objects.create(**validated_data)


class EpicCreateSerializer(BaseSerializer):
    """
    Serializer for creating epics with member validation and date checking.
    """

    members = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Epic
        fields = [
            "name",
            "description",
            "start_date",
            "target_date",
            "status",
            "lead",
            "members",
            "initiative",
            "external_source",
            "external_id",
        ]
        read_only_fields = [
            "id",
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "deleted_at",
        ]

    def validate(self, data):
        project_id = self.context.get("project_id")
        if not project_id:
            raise serializers.ValidationError("Project ID is required")
        project = Project.objects.get(id=project_id)
        if not project:
            raise serializers.ValidationError("Project not found")
        if (
            data.get("start_date", None) is not None
            and data.get("target_date", None) is not None
            and data.get("start_date", None) > data.get("target_date", None)
        ):
            raise serializers.ValidationError("Start date cannot exceed target date")

        if data.get("members", []):
            data["members"] = ProjectMember.objects.filter(
                project_id=self.context.get("project_id"), member_id__in=data["members"]
            ).values_list("member_id", flat=True)

        return data

    def create(self, validated_data):
        members = validated_data.pop("members", None)

        project_id = self.context["project_id"]
        workspace_id = self.context["workspace_id"]

        epic_name = validated_data.get("name")
        if epic_name:
            epic = Epic.objects.filter(name=epic_name, project_id=project_id).first()
            if epic:
                raise serializers.ValidationError(
                    {
                        "id": str(epic.id),
                        "code": "EPIC_NAME_ALREADY_EXISTS",
                        "error": "Epic with this name already exists",
                        "message": "Epic with this name already exists",
                    }
                )

        epic = Epic.objects.create(**validated_data, project_id=project_id)
        if members is not None:
            EpicMember.objects.bulk_create(
                [
                    EpicMember(
                        epic=epic,
                        member_id=str(member),
                        project_id=project_id,
                        workspace_id=workspace_id,
                        created_by=epic.created_by,
                        updated_by=epic.updated_by,
                    )
                    for member in members
                ],
                batch_size=10,
                ignore_conflicts=True,
            )

        return epic


class EpicUpdateSerializer(EpicCreateSerializer):
    """
    Serializer for updating epics.
    """

    class Meta(EpicCreateSerializer.Meta):
        model = Epic
        fields = EpicCreateSerializer.Meta.fields + [
            "members",
        ]
        read_only_fields = EpicCreateSerializer.Meta.read_only_fields

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        epic_name = validated_data.get("name")
        if epic_name:
            if Epic.objects.filter(name=epic_name, project=instance.project).exclude(id=instance.id).exists():
                raise serializers.ValidationError({"error": "Epic with this name already exists"})

        if members is not None:
            EpicMember.objects.filter(epic=instance).delete()
            EpicMember.objects.bulk_create(
                [
                    EpicMember(
                        epic=instance,
                        member_id=str(member),
                        project=instance.project,
                        workspace=instance.project.workspace,
                        created_by=instance.created_by,
                        updated_by=instance.updated_by,
                    )
                    for member in members
                ],
                batch_size=10,
                ignore_conflicts=True,
            )

        return super().update(instance, validated_data)


class EpicSerializer(BaseSerializer):
    """
    Comprehensive epic serializer with issue metrics and member management.
    """

    members = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        required=False,
    )
    total_issues = serializers.IntegerField(read_only=True)
    cancelled_issues = serializers.IntegerField(read_only=True)
    completed_issues = serializers.IntegerField(read_only=True)
    started_issues = serializers.IntegerField(read_only=True)
    unstarted_issues = serializers.IntegerField(read_only=True)
    backlog_issues = serializers.IntegerField(read_only=True)

    class Meta:
        model = Epic
        fields = "__all__"
        read_only_fields = [
            "id",
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "deleted_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["members"] = [str(member.id) for member in instance.members.all()]
        return data


class EpicLiteSerializer(BaseSerializer):
    """
    Lightweight epic serializer for minimal data transfer.
    """

    class Meta:
        model = Epic
        fields = "__all__"


class EpicIssueSerializer(BaseSerializer):
    """
    Serializer for epic-issue relationships.
    """

    sub_issues_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = EpicIssue
        fields = "__all__"
        read_only_fields = [
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "epic",
        ]


class EpicLinkSerializer(BaseSerializer):
    """
    Serializer for epic external links.
    """

    class Meta:
        model = EpicLink
        fields = "__all__"
        read_only_fields = [
            "workspace",
            "project",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "epic",
        ]

    def create(self, validated_data):
        if EpicLink.objects.filter(url=validated_data.get("url"), epic_id=validated_data.get("epic_id")).exists():
            raise serializers.ValidationError({"error": "URL already exists for this Epic"})
        return EpicLink.objects.create(**validated_data)


class EpicIssueRequestSerializer(serializers.Serializer):
    """
    Serializer for bulk work item assignment to epics.
    """

    issues = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of issue IDs to add to the epic",
    )
