# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Third Party imports
from rest_framework import serializers

# Module imports
from .base import BaseSerializer
from .user import UserLiteSerializer
from .state import StateLiteSerializer
from .project import ProjectLiteSerializer
from .issue import IssueFlatSerializer, LabelLiteSerializer
from plane.db.models import Issue, IntakeIssue, Intake


class IntakeFormSubmissionSerializer(BaseSerializer):
    """
    Serializer for intake form field submissions.
    Handles dynamic field values from the form.
    """

    # Honeypot field for basic bot detection
    website_url = serializers.CharField(required=False, allow_blank=True, default="")
    hp_field = serializers.CharField(required=False, allow_blank=True, default="")

    # Captcha token (optional - can be required via settings)
    captcha_token = serializers.CharField(required=False, allow_blank=True, default=None)

    class Meta:
        fields = ["fields", "website_url", "hp_field", "captcha_token"]

    def validate_fields(self, value):
        """
        Validate the dynamic fields submitted.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Fields must be a dictionary")
        return value


class IntakeFormConfigSerializer(BaseSerializer):
    """
    Serializer for public intake form configuration.
    """

    class Meta:
        model = Intake
        fields = ["id", "name", "description", "field_config_json", "is_active", "captcha_enabled", "rate_limit"]


class IntakeIssueSerializer(BaseSerializer):
    issue_detail = IssueFlatSerializer(source="issue", read_only=True)
    project_detail = ProjectLiteSerializer(source="project", read_only=True)

    class Meta:
        model = IntakeIssue
        fields = "__all__"
        read_only_fields = ["project", "workspace"]


class IntakeIssueLiteSerializer(BaseSerializer):
    class Meta:
        model = IntakeIssue
        fields = ["id", "status", "duplicate_to", "snoozed_till", "source"]
        read_only_fields = fields


class IssueStateIntakeSerializer(BaseSerializer):
    state_detail = StateLiteSerializer(read_only=True, source="state")
    project_detail = ProjectLiteSerializer(read_only=True, source="project")
    label_details = LabelLiteSerializer(read_only=True, source="labels", many=True)
    assignee_details = UserLiteSerializer(read_only=True, source="assignees", many=True)
    sub_issues_count = serializers.IntegerField(read_only=True)
    bridge_id = serializers.UUIDField(read_only=True)
    issue_intake = IntakeIssueLiteSerializer(read_only=True, many=True)

    class Meta:
        model = Issue
        fields = "__all__"
