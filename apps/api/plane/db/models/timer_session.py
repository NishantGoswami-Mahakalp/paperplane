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


class TimerSession(ProjectBaseModel):
    item = models.ForeignKey(
        "db.Issue",
        on_delete=models.CASCADE,
        related_name="timer_sessions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="timer_sessions",
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    is_running = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Timer Session"
        verbose_name_plural = "Timer Sessions"
        db_table = "timer_sessions"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "is_running"]),
            models.Index(fields=["workspace", "user", "is_running"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "user", "is_running"],
                condition=models.Q(is_running=True),
                name="unique_running_timer_per_user_per_workspace",
            ),
        ]
