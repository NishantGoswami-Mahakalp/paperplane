# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path

from plane.app.views import (
    WorkLogViewSet,
    WorkLogListEndpoint,
    TimerStartEndpoint,
    TimerStopEndpoint,
    TimerDetailEndpoint,
    WorklogTimeReportsEndpoint,
    WorklogExportEndpoint,
)

urlpatterns = [
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/worklogs/",
        WorkLogViewSet.as_view({"get": "list", "post": "create"}),
        name="item-worklogs",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/worklogs/<uuid:pk>/",
        WorkLogViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="item-worklogs-detail",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/timer/start/",
        TimerStartEndpoint.as_view(),
        name="timer-start",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/timer/stop/",
        TimerStopEndpoint.as_view(),
        name="timer-stop",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/timer/",
        TimerDetailEndpoint.as_view(),
        name="timer-detail",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/worklogs/reports/",
        WorklogTimeReportsEndpoint.as_view(),
        name="worklog-reports",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/worklogs/export/",
        WorklogExportEndpoint.as_view(),
        name="worklog-export",
    ),
]
