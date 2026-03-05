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


class Template(BaseModel):
    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="templates",
    )
    project = models.ForeignKey(
        "db.Project",
        on_delete=models.CASCADE,
        related_name="templates",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    entity_type = models.CharField(
        max_length=30,
        choices=TemplateType.CHOICES,
        default=TemplateType.WORK_ITEM,
    )
    schema_version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        db_table = "templates"
        ordering = ("-created_at",)
        unique_together = ["workspace", "project", "name", "entity_type"]

    def __str__(self):
        return f"{self.name} ({self.entity_type})"


class TemplateField(BaseModel):
    FIELD_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        ("date", "Date"),
        ("select", "Select"),
        ("multiselect", "MultiSelect"),
        ("boolean", "Boolean"),
        ("user", "User"),
        ("url", "URL"),
    ]

    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="fields",
    )
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=30, choices=FIELD_TYPES)
    description = models.TextField(blank=True)
    default_value = models.JSONField(default=dict, blank=True)
    options = models.JSONField(default=list, blank=True)
    is_required = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Template Field"
        verbose_name_plural = "Template Fields"
        db_table = "template_fields"
        ordering = ("sort_order",)

    def __str__(self):
        return f"{self.template.name} - {self.name}"


class TemplateVersion(BaseModel):
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    schema_version = models.PositiveIntegerField()
    fields_snapshot = models.JSONField(default=list)
    content_snapshot = models.JSONField(default=dict)
    change_summary = models.TextField(blank=True)

    class Meta:
        verbose_name = "Template Version"
        verbose_name_plural = "Template Versions"
        db_table = "template_versions"
        ordering = ("-version",)
        unique_together = ["template", "version"]

    def __str__(self):
        return f"{self.template.name} v{self.version}"

    @classmethod
    def create_version(cls, template, change_summary=""):
        fields = list(
            template.fields.values(
                "id", "name", "field_type", "description", "default_value", "options", "is_required", "sort_order"
            )
        )
        content = {
            "name": template.name,
            "description": template.description,
            "entity_type": template.entity_type,
        }
        last_version = template.versions.first()
        new_version = (last_version.version + 1) if last_version else 1

        return cls.objects.create(
            template=template,
            version=new_version,
            name=template.name,
            description=template.description,
            schema_version=template.schema_version,
            fields_snapshot=fields,
            content_snapshot=content,
            change_summary=change_summary,
        )


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
