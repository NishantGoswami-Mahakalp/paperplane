# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path

from plane.app.views.customer.base import (
    CustomerViewSet,
    CustomerContactViewSet,
    CustomerIssuesViewSet,
)

urlpatterns = [
    path(
        "workspaces/<str:slug>/customers/",
        CustomerViewSet.as_view({"get": "list", "post": "create"}),
        name="workspace-customers",
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:pk>/",
        CustomerViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="workspace-customer",
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:customer_id>/contacts/",
        CustomerContactViewSet.as_view({"get": "list", "post": "create"}),
        name="workspace-customer-contacts",
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:customer_id>/contacts/<uuid:pk>/",
        CustomerContactViewSet.as_view(
            {
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="workspace-customer-contact",
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:customer_id>/issues/",
        CustomerIssuesViewSet.as_view({"get": "list"}),
        name="workspace-customer-issues",
    ),
]
