# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Third party frameworks
from rest_framework import serializers

# Module imports
from plane.db.models import Customer, CustomerContact
from .base import BaseSerializer
from .label import LabelSerializer


class CustomerContactSerializer(BaseSerializer):
    class Meta:
        model = CustomerContact
        fields = "__all__"
        read_only_fields = ["customer"]


class CustomerContactLiteSerializer(BaseSerializer):
    class Meta:
        model = CustomerContact
        fields = ["id", "name", "email", "phone", "role", "is_primary"]


class CustomerSerializer(BaseSerializer):
    contacts = CustomerContactSerializer(many=True, read_only=True)
    tags_details = LabelSerializer(source="tags", many=True, read_only=True)
    issue_count = serializers.IntegerField(read_only=True)
    open_issue_count = serializers.IntegerField(read_only=True)
    closed_issue_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ["workspace"]


class CustomerLiteSerializer(BaseSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "email",
            "status",
            "external_source",
            "external_id",
            "created_at",
            "updated_at",
        ]


class CustomerListSerializer(BaseSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "email",
            "status",
            "description",
            "external_source",
            "external_id",
            "metadata",
            "created_at",
            "updated_at",
        ]
