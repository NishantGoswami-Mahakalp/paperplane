# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
from uuid import uuid4

# Django imports
from django.conf import settings
from django.db import models

# Module imports
from .base import BaseModel
from .project import ProjectBaseModel


class WorkLog(ProjectBaseModel):
    item = models.ForeignKey(
        "db.Issue",
        on_delete=models.CASCADE,
        related_name="worklogs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="worklogs",
    )
    duration_minutes = models.IntegerField()
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Work Log"
        verbose_name_plural = "Work Logs"
        db_table = "work_logs"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["item", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]
