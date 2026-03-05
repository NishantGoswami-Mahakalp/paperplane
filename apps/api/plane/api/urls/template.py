# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path

from plane.api.views import (
    IssueTemplateListCreateAPIEndpoint,
    IssueTemplateDetailAPIEndpoint,
    IssueTemplateInstantiateAPIEndpoint,
    PageTemplateListCreateAPIEndpoint,
    PageTemplateDetailAPIEndpoint,
    PageTemplateInstantiateAPIEndpoint,
    TemplateListCreateAPIEndpoint,
    TemplateDetailAPIEndpoint,
    TemplateVersionListAPIEndpoint,
    TemplateVersionRestoreAPIEndpoint,
    TemplateExportAPIEndpoint,
    TemplateImportAPIEndpoint,
)


urlpatterns = [
    # Issue Template URLs
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issue-templates/",
        IssueTemplateListCreateAPIEndpoint.as_view(http_method_names=["get", "post"]),
        name="issue-template-list",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issue-templates/<uuid:template_id>/",
        IssueTemplateDetailAPIEndpoint.as_view(http_method_names=["get", "delete"]),
        name="issue-template-detail",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/issue-templates/<uuid:template_id>/instantiate/",
        IssueTemplateInstantiateAPIEndpoint.as_view(http_method_names=["post"]),
        name="issue-template-instantiate",
    ),
    # Page Template URLs
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/page-templates/",
        PageTemplateListCreateAPIEndpoint.as_view(http_method_names=["get", "post"]),
        name="page-template-list",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/page-templates/<uuid:template_id>/",
        PageTemplateDetailAPIEndpoint.as_view(http_method_names=["get", "delete"]),
        name="page-template-detail",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/page-templates/<uuid:template_id>/instantiate/",
        PageTemplateInstantiateAPIEndpoint.as_view(http_method_names=["post"]),
        name="page-template-instantiate",
    ),
    # New Versioned Template URLs
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/templates/",
        TemplateListCreateAPIEndpoint.as_view(http_method_names=["get", "post"]),
        name="template-list",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/templates/<uuid:template_id>/",
        TemplateDetailAPIEndpoint.as_view(http_method_names=["get", "patch", "delete"]),
        name="template-detail",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/templates/<uuid:template_id>/versions/",
        TemplateVersionListAPIEndpoint.as_view(http_method_names=["get"]),
        name="template-version-list",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/templates/<uuid:template_id>/versions/<uuid:version_id>/restore/",
        TemplateVersionRestoreAPIEndpoint.as_view(http_method_names=["post"]),
        name="template-version-restore",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/templates/<uuid:template_id>/export/",
        TemplateExportAPIEndpoint.as_view(http_method_names=["get"]),
        name="template-export",
    ),
    path(
        "workspaces/<str:slug>/projects/<uuid:project_id>/templates/import/",
        TemplateImportAPIEndpoint.as_view(http_method_names=["post"]),
        name="template-import",
    ),
]
