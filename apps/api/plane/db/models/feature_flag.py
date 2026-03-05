# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.db import models
from .base import BaseModel
from .user import User


class FeatureFlag(BaseModel):
    """
    Feature flags at different levels (workspace, project, user)
    """

    class Level(models.TextChoices):
        WORKSPACE = "WORKSPACE", "Workspace"
        PROJECT = "PROJECT", "Project"
        USER = "USER", "User"

    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.WORKSPACE,
    )
    is_default = models.BooleanField(default=False)
    default_enabled = models.BooleanField(default=False)

    class Meta:
        app_label = "db"
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"

    def __str__(self):
        return f"{self.name} ({self.key})"


class FeatureFlagValue(BaseModel):
    """
    Stores feature flag values for workspaces, projects, and users
    """

    class Level(models.TextChoices):
        WORKSPACE = "WORKSPACE", "Workspace"
        PROJECT = "PROJECT", "Project"
        USER = "USER", "User"

    feature_flag = models.ForeignKey(
        FeatureFlag,
        on_delete=models.CASCADE,
        related_name="values",
    )
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
    )
    entity_id = models.CharField(max_length=100)
    enabled = models.BooleanField(default=False)

    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="feature_flags",
    )
    project = models.ForeignKey(
        "db.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="feature_flags",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="feature_flags",
    )

    class Meta:
        app_label = "db"
        verbose_name = "Feature Flag Value"
        verbose_name_plural = "Feature Flag Values"
        unique_together = ["feature_flag", "level", "entity_id"]
        indexes = [
            models.Index(fields=["level", "entity_id"]),
            models.Index(fields=["workspace", "level"]),
            models.Index(fields=["project", "level"]),
            models.Index(fields=["user", "level"]),
        ]

    def __str__(self):
        return f"{self.feature_flag.name} - {self.level}:{self.entity_id} = {self.enabled}"
