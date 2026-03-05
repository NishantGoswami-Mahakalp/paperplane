# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path


from plane.space.views import (
    ProjectDeployBoardPublicSettingsEndpoint,
    ProjectIssuesPublicEndpoint,
    WorkspaceProjectAnchorEndpoint,
    ProjectCyclesEndpoint,
    ProjectModulesEndpoint,
    ProjectStatesEndpoint,
    ProjectLabelsEndpoint,
    ProjectMembersEndpoint,
    ProjectMetaDataEndpoint,
    ProjectItemDetailPublicEndpoint,
    ProjectItemCommentsPublicEndpoint,
    ProjectItemActivitiesPublicEndpoint,
    ProjectBoardPublicEndpoint,
    PageRetrievePublicEndpoint,
)

urlpatterns = [
    path(
        "anchor/<str:anchor>/meta/",
        ProjectMetaDataEndpoint.as_view(),
        name="project-meta",
    ),
    path(
        "anchor/<str:anchor>/settings/",
        ProjectDeployBoardPublicSettingsEndpoint.as_view(),
        name="project-deploy-board-settings",
    ),
    path(
        "anchor/<str:anchor>/board/",
        ProjectBoardPublicEndpoint.as_view(),
        name="project-public-board",
    ),
    path(
        "anchor/<str:anchor>/issues/",
        ProjectIssuesPublicEndpoint.as_view(),
        name="project-deploy-board",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/anchor/",
        WorkspaceProjectAnchorEndpoint.as_view(),
        name="project-deploy-board",
    ),
    path(
        "public/projects/<uuid:project_id>/items/<uuid:item_id>/",
        ProjectItemDetailPublicEndpoint.as_view(),
        name="project-item-detail-public",
    ),
    path(
        "public/projects/<uuid:project_id>/items/<uuid:item_id>/comments/",
        ProjectItemCommentsPublicEndpoint.as_view(),
        name="project-item-comments-public",
    ),
    path(
        "public/projects/<uuid:project_id>/items/<uuid:item_id>/activities/",
        ProjectItemActivitiesPublicEndpoint.as_view(),
        name="project-item-activities-public",
    ),
    path(
        "public/projects/<uuid:project_id>/pages/<uuid:page_id>/",
        PageRetrievePublicEndpoint.as_view(),
        name="project-page-detail-public",
    ),
    path(
        "anchor/<str:anchor>/cycles/",
        ProjectCyclesEndpoint.as_view(),
        name="project-cycles",
    ),
    path(
        "anchor/<str:anchor>/modules/",
        ProjectModulesEndpoint.as_view(),
        name="project-modules",
    ),
    path(
        "anchor/<str:anchor>/states/",
        ProjectStatesEndpoint.as_view(),
        name="project-states",
    ),
    path(
        "anchor/<str:anchor>/labels/",
        ProjectLabelsEndpoint.as_view(),
        name="project-labels",
    ),
    path(
        "anchor/<str:anchor>/members/",
        ProjectMembersEndpoint.as_view(),
        name="project-members",
    ),
]
