# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Module imports
from plane.db.models import Customer, CustomerContact, CustomerComment, Label
from rest_framework import serializers

from .base import BaseSerializer


class CustomerCommentSerializer(BaseSerializer):
    class Meta:
        model = CustomerComment
        fields = "__all__"
        read_only_fields = [
            "id",
            "customer",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


class CustomerContactSerializer(BaseSerializer):
    class Meta:
        model = CustomerContact
        fields = "__all__"
        read_only_fields = [
            "id",
            "customer",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


class CustomerContactLiteSerializer(BaseSerializer):
    class Meta:
        model = CustomerContact
        fields = ["id", "name", "email", "phone", "role", "is_primary"]


class CustomerSerializer(BaseSerializer):
    tags = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Label.objects.values_list("id", flat=True)),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = [
            "id",
            "workspace",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


class CustomerLiteSerializer(BaseSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "email", "company"]
