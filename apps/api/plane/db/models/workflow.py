# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.db import models
from django.db.models import Q

# Module imports
from .project import ProjectBaseModel


class WorkflowState(ProjectBaseModel):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    position = models.FloatField(default=65535)
    item_type = models.ForeignKey(
        "db.ProjectIssueType",
        related_name="workflow_states",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Workflow State"
        verbose_name_plural = "Workflow States"
        db_table = "workflow_states"
        unique_together = ["name", "project", "item_type", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "project", "item_type"],
                condition=Q(deleted_at__isnull=True),
                name="workflow_state_unique_name_project_item_type_when_deleted_at_null",
            )
        ]
        ordering = ("position",)

    def __str__(self):
        type_str = f" ({self.item_type.issue_type.name})" if self.item_type else ""
        return f"{self.name} <{self.project.name}>{type_str}"

    def save(self, *args, **kwargs):
        if self._state.adding and self.position is None:
            last_position = WorkflowState.objects.filter(
                project=self.project,
                item_type=self.item_type,
            ).aggregate(models.Max("position"))["position__max"]
            if last_position is not None:
                self.position = last_position + 10000
        super().save(*args, **kwargs)


class WorkflowTransition(ProjectBaseModel):
    name = models.CharField(max_length=255)
    from_state = models.ForeignKey(
        "db.WorkflowState",
        related_name="transitions_from",
        on_delete=models.CASCADE,
    )
    to_state = models.ForeignKey(
        "db.WorkflowState",
        related_name="transitions_to",
        on_delete=models.CASCADE,
    )
    condition_json = models.JSONField(default=dict, blank=True)
    item_type = models.ForeignKey(
        "db.ProjectIssueType",
        related_name="workflow_transitions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Workflow Transition"
        verbose_name_plural = "Workflow Transitions"
        db_table = "workflow_transitions"
        unique_together = ["name", "project", "item_type", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "project", "item_type"],
                condition=Q(deleted_at__isnull=True),
                name="workflow_transition_unique_name_project_item_type_when_deleted_at_null",
            )
        ]

    def __str__(self):
        type_str = f" ({self.item_type.issue_type.name})" if self.item_type else ""
        return f"{self.from_state.name} -> {self.to_state.name} <{self.project.name}>{type_str}"
