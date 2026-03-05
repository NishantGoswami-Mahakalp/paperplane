# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
from uuid import uuid4

# Django imports
from django.db import models
from django.db.models import Q

# Module imports
from .project import ProjectBaseModel
from .base import BaseModel


class WorkItemType(BaseModel):
    WORK_ITEM_TYPES = [
        ("task", "Task"),
        ("bug", "Bug"),
        ("story", "Story"),
    ]

    SCHEMA_VERSION = 1

    workspace = models.ForeignKey("db.Workspace", related_name="work_item_types", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    work_item_type = models.CharField(max_length=50, choices=WORK_ITEM_TYPES, default="task")
    logo_props = models.JSONField(default=dict)
    is_epic = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    schema_version = models.PositiveIntegerField(default=SCHEMA_VERSION)
    external_source = models.CharField(max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Work Item Type"
        verbose_name_plural = "Work Item Types"
        db_table = "work_item_types"
        unique_together = [["workspace", "name", "deleted_at"]]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "name"],
                condition=Q(deleted_at__isnull=True),
                name="work_item_type_unique_name_workspace_when_deleted_at_null",
            )
        ]

    def __str__(self):
        return self.name


class ProjectWorkItemType(ProjectBaseModel):
    work_item_type = models.ForeignKey(
        "db.WorkItemType", related_name="project_work_item_types", on_delete=models.CASCADE
    )
    position = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ["project", "work_item_type", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "work_item_type"],
                condition=Q(deleted_at__isnull=True),
                name="project_work_item_type_unique_project_work_item_type_when_deleted_at_null",
            )
        ]
        verbose_name = "Project Work Item Type"
        verbose_name_plural = "Project Work Item Types"
        db_table = "project_work_item_types"
        ordering = ("project", "position")

    def __str__(self):
        return f"{self.project} - {self.work_item_type}"


class FieldDefinition(BaseModel):
    FIELD_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        ("select", "Select"),
        ("multiselect", "MultiSelect"),
        ("date", "Date"),
        ("email", "Email"),
        ("url", "URL"),
        ("checkbox", "Checkbox"),
        ("user", "User"),
        ("users", "Users"),
        ("relation", "Relation"),
        ("rich_text", "Rich Text"),
    ]

    workspace = models.ForeignKey("db.Workspace", related_name="field_definitions", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    validation_rules = models.JSONField(default=dict)
    options = models.JSONField(default=list)
    external_source = models.CharField(max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Field Definition"
        verbose_name_plural = "Field Definitions"
        db_table = "field_definitions"
        unique_together = [["workspace", "name", "deleted_at"]]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "name"],
                condition=Q(deleted_at__isnull=True),
                name="field_definition_unique_name_workspace_when_deleted_at_null",
            )
        ]
        ordering = ("position",)

    def __str__(self):
        return self.name


class WorkItemTypeField(BaseModel):
    work_item_type = models.ForeignKey(
        "db.WorkItemType", related_name="work_item_type_fields", on_delete=models.CASCADE
    )
    field_definition = models.ForeignKey(
        "db.FieldDefinition", related_name="work_item_type_fields", on_delete=models.CASCADE
    )
    is_required = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    validations = models.JSONField(default=dict)

    class Meta:
        unique_together = ["work_item_type", "field_definition", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["work_item_type", "field_definition"],
                condition=Q(deleted_at__isnull=True),
                name="work_item_type_field_unique_work_item_type_field_when_deleted_at_null",
            )
        ]
        verbose_name = "Work Item Type Field"
        verbose_name_plural = "Work Item Type Fields"
        db_table = "work_item_type_fields"
        ordering = ("position",)

    def __str__(self):
        return f"{self.work_item_type.name} - {self.field_definition.name}"


def get_default_work_item_fields(work_item_type: str) -> list:
    base_fields = [
        {
            "field_name": "name",
            "field_type": "text",
            "is_required": True,
            "position": 0,
            "validations": {"max_length": 255},
        },
        {
            "field_name": "description",
            "field_type": "rich_text",
            "is_required": False,
            "position": 1,
            "validations": {},
        },
        {
            "field_name": "state",
            "field_type": "select",
            "is_required": True,
            "position": 2,
            "validations": {},
        },
        {
            "field_name": "priority",
            "field_type": "select",
            "is_required": False,
            "position": 3,
            "validations": {},
        },
        {
            "field_name": "assignees",
            "field_type": "users",
            "is_required": False,
            "position": 4,
            "validations": {},
        },
        {
            "field_name": "start_date",
            "field_type": "date",
            "is_required": False,
            "position": 5,
            "validations": {},
        },
        {
            "field_name": "target_date",
            "field_type": "date",
            "is_required": False,
            "position": 6,
            "validations": {},
        },
        {
            "field_name": "labels",
            "field_type": "multiselect",
            "is_required": False,
            "position": 7,
            "validations": {},
        },
    ]

    if work_item_type == "bug":
        return base_fields + [
            {
                "field_name": "severity",
                "field_type": "select",
                "is_required": False,
                "position": 8,
                "validations": {"options": ["critical", "high", "medium", "low"]},
            },
            {
                "field_name": "affects_version",
                "field_type": "text",
                "is_required": False,
                "position": 9,
                "validations": {},
            },
        ]
    elif work_item_type == "story":
        return base_fields + [
            {
                "field_name": "story_points",
                "field_type": "number",
                "is_required": False,
                "position": 8,
                "validations": {"min": 0, "max": 100},
            },
            {
                "field_name": "acceptance_criteria",
                "field_type": "rich_text",
                "is_required": False,
                "position": 9,
                "validations": {},
            },
        ]

    return base_fields


class IssueType(BaseModel):
    workspace = models.ForeignKey("db.Workspace", related_name="issue_types", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo_props = models.JSONField(default=dict)
    is_epic = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    level = models.FloatField(default=0)
    external_source = models.CharField(max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Issue Type"
        verbose_name_plural = "Issue Types"
        db_table = "issue_types"

    def __str__(self):
        return self.name


class ProjectIssueType(ProjectBaseModel):
    issue_type = models.ForeignKey("db.IssueType", related_name="project_issue_types", on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ["project", "issue_type", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "issue_type"],
                condition=Q(deleted_at__isnull=True),
                name="project_issue_type_unique_project_issue_type_when_deleted_at_null",
            )
        ]
        verbose_name = "Project Issue Type"
        verbose_name_plural = "Project Issue Types"
        db_table = "project_issue_types"
        ordering = ("project", "issue_type")

    def __str__(self):
        return f"{self.project} - {self.issue_type}"
