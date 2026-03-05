# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path

from plane.app.views import (
    WorkItemTypeViewSet,
    FieldDefinitionViewSet,
    ProjectWorkItemTypeViewSet,
    WorkItemTypeFieldViewSet,
)


urlpatterns = [
    path(
        "workspaces/<str:slug>/work-item-types/",
        WorkItemTypeViewSet.as_view({"get": "list", "post": "create"}),
        name="work-item-type",
    ),
    path(
        "workspaces/<str:slug>/work-item-types/<uuid:pk>/",
        WorkItemTypeViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="work-item-type",
    ),
    path(
        "workspaces/<str:slug>/field-definitions/",
        FieldDefinitionViewSet.as_view({"get": "list", "post": "create"}),
        name="field-definition",
    ),
    path(
        "workspaces/<str:slug>/field-definitions/<uuid:pk>/",
        FieldDefinitionViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="field-definition",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/work-item-types/",
        ProjectWorkItemTypeViewSet.as_view({"get": "list", "post": "create"}),
        name="project-work-item-type",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/work-item-types/<uuid:pk>/",
        ProjectWorkItemTypeViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="project-work-item-type",
    ),
    path(
        "workspaces/<str:slug>/work-item-types/<uuid:work_item_type_id>/fields/",
        WorkItemTypeFieldViewSet.as_view({"get": "list", "post": "create"}),
        name="work-item-type-field",
    ),
    path(
        "workspaces/<str:slug>/work-item-types/<uuid:work_item_type_id>/fields/<uuid:pk>/",
        WorkItemTypeFieldViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="work-item-type-field",
    ),
]
