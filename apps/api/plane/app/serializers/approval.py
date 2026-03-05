# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Third party imports
from rest_framework import serializers

# Module imports
from plane.app.serializers import BaseSerializer
from plane.db.models import (
    ApprovalPolicy,
    ApprovalPolicyApprover,
    ApprovalDecision,
)


class ApprovalPolicyApproverSerializer(BaseSerializer):
    class Meta:
        model = ApprovalPolicyApprover
        fields = [
            "id",
            "policy",
            "approver",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ApprovalPolicySerializer(BaseSerializer):
    class Meta:
        model = ApprovalPolicy
        fields = [
            "id",
            "name",
            "description",
            "project",
            "workspace",
            "issue_type",
            "type",
            "required_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ApprovalPolicyLiteSerializer(BaseSerializer):
    class Meta:
        model = ApprovalPolicy
        fields = [
            "id",
            "name",
            "description",
            "type",
            "required_count",
            "is_active",
        ]


class ApprovalDecisionSerializer(BaseSerializer):
    class Meta:
        model = ApprovalDecision
        fields = [
            "id",
            "policy",
            "item_id",
            "requested_by",
            "approver",
            "status",
            "comment",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ApprovalDecisionLiteSerializer(BaseSerializer):
    class Meta:
        model = ApprovalDecision
        fields = [
            "id",
            "policy",
            "item_id",
            "approver",
            "status",
            "order",
        ]


class ApprovalApproveSerializer(BaseSerializer):
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class ApprovalRejectSerializer(BaseSerializer):
    comment = serializers.CharField(required=True, allow_blank=False)


class ApprovalReassignSerializer(BaseSerializer):
    approver_id = serializers.UUIDField(required=True)
