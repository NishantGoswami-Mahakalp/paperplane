# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.db import models
from django.conf import settings

from .base import BaseModel
from .workspace import WorkspaceBaseModel
from .page import Page


class TemplateType:
    WORK_ITEM = "work_item"
    PAGE = "page"

    CHOICES = [
        (WORK_ITEM, "Work Item"),
        (PAGE, "Page"),
    ]


class IssueTemplate(BaseModel):
    PRIORITY_CHOICES = (
        ("urgent", "Urgent"),
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
        ("none", "None"),
    )

    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="issue_templates",
    )
    project = models.ForeignKey(
        "db.Project",
        on_delete=models.CASCADE,
        related_name="issue_templates",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    description_html = models.TextField(blank=True, default="<p></p>")
    description_json = models.JSONField(default=dict, blank=True)
    description_binary = models.BinaryField(null=True, blank=True)

    priority = models.CharField(
        max_length=30,
        choices=PRIORITY_CHOICES,
        default="none",
    )
    state = models.ForeignKey(
        "db.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issue_templates",
    )
    type = models.ForeignKey(
        "db.IssueType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issue_templates",
    )
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    estimate_point = models.ForeignKey(
        "db.EstimatePoint",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issue_templates",
    )

    labels = models.ManyToManyField(
        "db.Label",
        blank=True,
        related_name="issue_templates",
        through="IssueTemplateLabel",
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="issue_templates",
        through="IssueTemplateAssignee",
    )

    external_id = models.CharField(max_length=255, null=True, blank=True)
    external_source = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Issue Template"
        verbose_name_plural = "Issue Templates"
        db_table = "issue_templates"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class IssueTemplateLabel(models.Model):
    template = models.ForeignKey(IssueTemplate, on_delete=models.CASCADE)
    label = models.ForeignKey("db.Label", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("template", "label")
        db_table = "issue_template_labels"


class IssueTemplateAssignee(models.Model):
    template = models.ForeignKey(IssueTemplate, on_delete=models.CASCADE)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("template", "assignee")
        db_table = "issue_template_assignees"


class PageTemplate(BaseModel):
    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="page_templates",
    )
    project = models.ForeignKey(
        "db.Project",
        on_delete=models.CASCADE,
        related_name="page_templates",
        null=True,
        blank=True,
    )
    name = models.TextField(blank=True)
    description_json = models.JSONField(default=dict, blank=True)
    description_binary = models.BinaryField(null=True, blank=True)
    description_html = models.TextField(blank=True, default="<p></p>")
    description_stripped = models.TextField(blank=True, null=True)

    color = models.CharField(max_length=255, blank=True)

    labels = models.ManyToManyField(
        "db.Label",
        blank=True,
        related_name="page_templates",
        through="PageTemplateLabel",
    )

    access = models.PositiveSmallIntegerField(
        choices=Page.ACCESS_CHOICES,
        default=Page.PRIVATE_ACCESS,
    )
    is_locked = models.BooleanField(default=False)
    view_props = models.JSONField(default=dict)
    logo_props = models.JSONField(default=dict)

    external_id = models.CharField(max_length=255, null=True, blank=True)
    external_source = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Page Template"
        verbose_name_plural = "Page Templates"
        db_table = "page_templates"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from plane.utils.html_processor import strip_tags

        self.description_stripped = (
            None
            if (self.description_html == "" or self.description_html is None)
            else strip_tags(self.description_html)
        )
        super(PageTemplate, self).save(*args, **kwargs)


class PageTemplateLabel(models.Model):
    template = models.ForeignKey(PageTemplate, on_delete=models.CASCADE)
    label = models.ForeignKey("db.Label", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("template", "label")
        db_table = "page_template_labels"
