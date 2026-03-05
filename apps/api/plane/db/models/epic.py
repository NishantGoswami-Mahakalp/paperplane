# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.conf import settings
from django.db import models
from django.db.models import Q

# Module imports
from .project import ProjectBaseModel


def get_default_filters():
    return {
        "priority": None,
        "state": None,
        "state_group": None,
        "assignees": None,
        "created_by": None,
        "labels": None,
        "start_date": None,
        "target_date": None,
        "subscriber": None,
    }


def get_default_display_filters():
    return {
        "group_by": None,
        "order_by": "-created_at",
        "type": None,
        "sub_issue": True,
        "show_empty_groups": True,
        "layout": "list",
        "calendar_date_range": "",
    }


def get_default_display_properties():
    return {
        "assignee": True,
        "attachment_count": True,
        "created_on": True,
        "due_date": True,
        "estimate": True,
        "key": True,
        "labels": True,
        "link": True,
        "priority": True,
        "start_date": True,
        "state": True,
        "sub_issue_count": True,
        "updated_on": True,
    }


class EpicStatus(models.TextChoices):
    BACKLOG = "backlog"
    PLANNED = "planned"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Epic(ProjectBaseModel):
    name = models.CharField(max_length=255, verbose_name="Epic Name")
    description = models.TextField(verbose_name="Epic Description", blank=True)
    description_text = models.JSONField(verbose_name="Epic Description RT", blank=True, null=True)
    description_html = models.JSONField(verbose_name="Epic Description HTML", blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        choices=(
            ("backlog", "Backlog"),
            ("planned", "Planned"),
            ("in-progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ),
        default="planned",
        max_length=20,
    )
    lead = models.ForeignKey("db.User", on_delete=models.SET_NULL, related_name="epic_leads", null=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="epic_members",
        through="EpicMember",
        through_fields=("epic", "member"),
    )
    initiative = models.ForeignKey(
        "db.Initiative",
        on_delete=models.CASCADE,
        related_name="epics",
        null=True,
        blank=True,
    )
    view_props = models.JSONField(default=dict)
    sort_order = models.FloatField(default=65535)
    external_source = models.CharField(max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=255, blank=True, null=True)
    archived_at = models.DateTimeField(null=True)
    logo_props = models.JSONField(default=dict)

    # Progress fields
    total_issues = models.PositiveIntegerField(default=0)
    completed_issues = models.PositiveIntegerField(default=0)
    backlog_issues = models.PositiveIntegerField(default=0)
    started_issues = models.PositiveIntegerField(default=0)
    unstarted_issues = models.PositiveIntegerField(default=0)
    cancelled_issues = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ["name", "project", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "project"],
                condition=Q(deleted_at__isnull=True),
                name="epic_unique_name_project_when_deleted_at_null",
            )
        ]
        verbose_name = "Epic"
        verbose_name_plural = "Epics"
        db_table = "epics"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if self._state.adding:
            smallest_sort_order = Epic.objects.filter(project=self.project).aggregate(
                smallest=models.Min("sort_order")
            )["smallest"]

            if smallest_sort_order is not None:
                self.sort_order = smallest_sort_order - 10000

        super(Epic, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.start_date} {self.target_date}"


class EpicMember(ProjectBaseModel):
    epic = models.ForeignKey("db.Epic", on_delete=models.CASCADE)
    member = models.ForeignKey("db.User", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["epic", "member", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["epic", "member"],
                condition=models.Q(deleted_at__isnull=True),
                name="epic_member_unique_epic_member_when_deleted_at_null",
            )
        ]
        verbose_name = "Epic Member"
        verbose_name_plural = "Epic Members"
        db_table = "epic_members"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.epic.name} {self.member}"


class EpicIssue(ProjectBaseModel):
    epic = models.ForeignKey("db.Epic", on_delete=models.CASCADE, related_name="epic_issue_items")
    issue = models.ForeignKey("db.Issue", on_delete=models.CASCADE, related_name="issue_epic")

    class Meta:
        unique_together = ["issue", "epic", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["issue", "epic"],
                condition=models.Q(deleted_at__isnull=True),
                name="epic_issue_unique_issue_epic_when_deleted_at_null",
            )
        ]
        verbose_name = "Epic Issue"
        verbose_name_plural = "Epic Issues"
        db_table = "epic_issues"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.epic.name} {self.issue.name}"


class EpicLink(ProjectBaseModel):
    title = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField()
    epic = models.ForeignKey(Epic, on_delete=models.CASCADE, related_name="link_epic")
    metadata = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Epic Link"
        verbose_name_plural = "Epic Links"
        db_table = "epic_links"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.epic.name} {self.url}"


class EpicUserProperties(ProjectBaseModel):
    epic = models.ForeignKey("db.Epic", on_delete=models.CASCADE, related_name="epic_user_properties")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="epic_user_properties",
    )
    filters = models.JSONField(default=get_default_filters)
    display_filters = models.JSONField(default=get_default_display_filters)
    display_properties = models.JSONField(default=get_default_display_properties)
    rich_filters = models.JSONField(default=dict)

    class Meta:
        unique_together = ["epic", "user", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["epic", "user"],
                condition=models.Q(deleted_at__isnull=True),
                name="epic_user_properties_unique_epic_user_when_deleted_at_null",
            )
        ]
        verbose_name = "Epic User Property"
        verbose_name_plural = "Epic User Properties"
        db_table = "epic_user_properties"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.epic.name} {self.user.email}"


class InitiativeStatus(models.TextChoices):
    BACKLOG = "backlog"
    PLANNED = "planned"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Initiative(ProjectBaseModel):
    name = models.CharField(max_length=255, verbose_name="Initiative Name")
    description = models.TextField(verbose_name="Initiative Description", blank=True)
    description_text = models.JSONField(verbose_name="Initiative Description RT", blank=True, null=True)
    description_html = models.JSONField(verbose_name="Initiative Description HTML", blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        choices=(
            ("backlog", "Backlog"),
            ("planned", "Planned"),
            ("in-progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ),
        default="planned",
        max_length=20,
    )
    lead = models.ForeignKey("db.User", on_delete=models.SET_NULL, related_name="initiative_leads", null=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="initiative_members",
        through="InitiativeMember",
        through_fields=("initiative", "member"),
    )
    view_props = models.JSONField(default=dict)
    sort_order = models.FloatField(default=65535)
    external_source = models.CharField(max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=255, blank=True, null=True)
    archived_at = models.DateTimeField(null=True)
    logo_props = models.JSONField(default=dict)

    # Progress fields
    total_epics = models.PositiveIntegerField(default=0)
    completed_epics = models.PositiveIntegerField(default=0)
    backlog_epics = models.PositiveIntegerField(default=0)
    started_epics = models.PositiveIntegerField(default=0)
    cancelled_epics = models.PositiveIntegerField(default=0)
    total_issues = models.PositiveIntegerField(default=0)
    completed_issues = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ["name", "project", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "project"],
                condition=Q(deleted_at__isnull=True),
                name="initiative_unique_name_project_when_deleted_at_null",
            )
        ]
        verbose_name = "Initiative"
        verbose_name_plural = "Initiatives"
        db_table = "initiatives"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if self._state.adding:
            smallest_sort_order = Initiative.objects.filter(project=self.project).aggregate(
                smallest=models.Min("sort_order")
            )["smallest"]

            if smallest_sort_order is not None:
                self.sort_order = smallest_sort_order - 10000

        super(Initiative, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.start_date} {self.target_date}"


class InitiativeMember(ProjectBaseModel):
    initiative = models.ForeignKey("db.Initiative", on_delete=models.CASCADE)
    member = models.ForeignKey("db.User", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["initiative", "member", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["initiative", "member"],
                condition=models.Q(deleted_at__isnull=True),
                name="initiative_member_unique_initiative_member_when_deleted_at_null",
            )
        ]
        verbose_name = "Initiative Member"
        verbose_name_plural = "Initiative Members"
        db_table = "initiative_members"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.initiative.name} {self.member}"


class InitiativeEpic(ProjectBaseModel):
    initiative = models.ForeignKey("db.Initiative", on_delete=models.CASCADE, related_name="initiative_epics")
    epic = models.ForeignKey("db.Epic", on_delete=models.CASCADE, related_name="epic_initiative")

    class Meta:
        unique_together = ["epic", "initiative", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["epic", "initiative"],
                condition=models.Q(deleted_at__isnull=True),
                name="initiative_epic_unique_epic_initiative_when_deleted_at_null",
            )
        ]
        verbose_name = "Initiative Epic"
        verbose_name_plural = "Initiative Epics"
        db_table = "initiative_epics"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.initiative.name} {self.epic.name}"


class InitiativeLink(ProjectBaseModel):
    title = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField()
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name="link_initiative")
    metadata = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Initiative Link"
        verbose_name_plural = "Initiative Links"
        db_table = "initiative_links"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.initiative.name} {self.url}"


class InitiativeUserProperties(ProjectBaseModel):
    initiative = models.ForeignKey("db.Initiative", on_delete=models.CASCADE, related_name="initiative_user_properties")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="initiative_user_properties",
    )
    filters = models.JSONField(default=get_default_filters)
    display_filters = models.JSONField(default=get_default_display_filters)
    display_properties = models.JSONField(default=get_default_display_properties)
    rich_filters = models.JSONField(default=dict)

    class Meta:
        unique_together = ["initiative", "user", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["initiative", "user"],
                condition=models.Q(deleted_at__isnull=True),
                name="initiative_user_properties_unique_initiative_user_when_deleted_at_null",
            )
        ]
        verbose_name = "Initiative User Property"
        verbose_name_plural = "Initiative User Properties"
        db_table = "initiative_user_properties"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.initiative.name} {self.user.email}"
