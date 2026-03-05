# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.db import models
from django.utils import timezone

# Module imports
from plane.db.models import ProjectBaseModel


class ReceivedEmail(ProjectBaseModel):
    """
    Model to track received emails for deduplication.
    Stores subject + sender hash to detect duplicates within a time window.
    """

    message_id = models.CharField(max_length=500, unique=True)
    subject_hash = models.CharField(max_length=64, db_index=True)
    sender_email = models.EmailField(max_length=255, db_index=True)
    project = models.ForeignKey(
        "db.Project",
        on_delete=models.CASCADE,
        related_name="received_emails",
    )
    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="received_emails",
    )
    intake_issue = models.ForeignKey(
        "db.IntakeIssue",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_emails",
    )
    received_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Received Email"
        verbose_name_plural = "Received Emails"
        db_table = "received_emails"
        ordering = ("-received_at",)
        indexes = [
            models.Index(fields=["subject_hash", "sender_email", "project"]),
            models.Index(fields=["received_at"]),
        ]

    def __str__(self):
        return f"{self.subject_hash[:8]}... from {self.sender_email}"
