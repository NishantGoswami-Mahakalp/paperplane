# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path
from plane.api.views.customer import (
    CustomerListCreateAPIEndpoint,
    CustomerDetailAPIEndpoint,
    CustomerContactsAPIEndpoint,
    CustomerContactDetailAPIEndpoint,
    CustomerItemsAPIEndpoint,
    CustomerCommentsAPIEndpoint,
    CustomerCommentDetailAPIEndpoint,
)

urlpatterns = [
    path(
        "workspaces/<str:slug>/customers/",
        CustomerListCreateAPIEndpoint.as_view(http_method_names=["get", "post"]),
        name="customer",
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:customer_id>/",
        CustomerDetailAPIEndpoint.as_view(http_method_names=["get", "patch", "delete"]),
        name="customer-detail",
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:customer_id>/contacts/",
        CustomerContactsAPIEndpoint.as_view(http_method_names=["get", "post"]),
        name="customer-contacts",
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:customer_id>/contacts/<uuid:contact_id>/",
        CustomerContactDetailAPIEndpoint.as_view(http_method_names=["get", "patch", "delete"]),
        name="customer-contact-detail",
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:customer_id>/items/",
        CustomerItemsAPIEndpoint.as_view(http_method_names=["get"]),
        name="customer-items",
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:customer_id>/comments/",
        CustomerCommentsAPIEndpoint.as_view(http_method_names=["get", "post"]),
        name="customer-comments",
    ),
    path(
        "workspaces/<str:slug>/customers/<uuid:customer_id>/comments/<uuid:comment_id>/",
        CustomerCommentDetailAPIEndpoint.as_view(http_method_names=["get", "patch", "delete"]),
        name="customer-comment-detail",
    ),
]
