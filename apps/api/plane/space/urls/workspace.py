# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path

from plane.space.views import WorkspacePublicEndpoint

urlpatterns = [
    path(
        "workspaces/<uuid:workspace_id>/",
        WorkspacePublicEndpoint.as_view(),
        name="workspace-public",
    ),
]
