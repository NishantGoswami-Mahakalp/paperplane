# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Third party imports
from rest_framework import serializers

# Module imports
from plane.app.serializers import UserLiteSerializer


class WorkLogSerializer(serializers.ModelSerializer):
    user = UserLiteSerializer(read_only=True)

    class Meta:
        model = None
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        from plane.db.models import WorkLog

        self.Meta.model = WorkLog
        super().__init__(*args, **kwargs)


class WorkLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        from plane.db.models import WorkLog

        self.Meta.model = WorkLog
        super().__init__(*args, **kwargs)
