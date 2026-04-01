# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path

from plane.api.views import (
    ProjectAgentContextAPIEndpoint,
    ProjectAgentCommentUpdatesAPIEndpoint,
    ProjectAgentUpdatesAPIEndpoint,
    ProjectReadyWorkItemsAPIEndpoint,
    WorkItemAgentContextAPIEndpoint,
)

urlpatterns = [
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/agent-context/",
        ProjectAgentContextAPIEndpoint.as_view(http_method_names=["get"]),
        name="project-agent-context",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/agent-ready-work-items/",
        ProjectReadyWorkItemsAPIEndpoint.as_view(http_method_names=["get"]),
        name="project-agent-ready-work-items",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/agent-updates/",
        ProjectAgentUpdatesAPIEndpoint.as_view(http_method_names=["get"]),
        name="project-agent-updates",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/agent-comment-updates/",
        ProjectAgentCommentUpdatesAPIEndpoint.as_view(http_method_names=["get"]),
        name="project-agent-comment-updates",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/work-items/<uuid:issue_id>/agent-context/",
        WorkItemAgentContextAPIEndpoint.as_view(http_method_names=["get"]),
        name="work-item-agent-context",
    ),
]
