# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path

from plane.app.views import (
    ApprovalPolicyViewSet,
    ApprovalDecisionViewSet,
    ApprovalRequestEndpoint,
    ApprovalApproveEndpoint,
    ApprovalRejectEndpoint,
    ApprovalReassignEndpoint,
)

urlpatterns = [
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/approval-policies/",
        ApprovalPolicyViewSet.as_view({"get": "list", "post": "create"}),
        name="project-approval-policies",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/approval-policies/<uuid:pk>/",
        ApprovalPolicyViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="project-approval-policies",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/approvals/",
        ApprovalDecisionViewSet.as_view({"get": "list"}),
        name="item-approvals",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/approvals/<uuid:pk>/",
        ApprovalDecisionViewSet.as_view({"get": "retrieve"}),
        name="item-approval-detail",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/request-approval/",
        ApprovalRequestEndpoint.as_view(),
        name="item-request-approval",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/approvals/<approval_id>/approve/",
        ApprovalApproveEndpoint.as_view(),
        name="item-approval-approve",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/approvals/<approval_id>/reject/",
        ApprovalRejectEndpoint.as_view(),
        name="item-approval-reject",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/items/<uuid:item_id>/approvals/<approval_id>/reassign/",
        ApprovalReassignEndpoint.as_view(),
        name="item-approval-reassign",
    ),
]
