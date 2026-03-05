# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

# Module imports
from .base import BaseModel
from .project import ProjectBaseModel


class ApprovalPolicy(BaseModel):
    class Type(models.TextChoices):
        SEQUENTIAL = "sequential", "Sequential"
        PARALLEL = "parallel", "Parallel"

    name = models.CharField(max_length=255, verbose_name="Policy Name")
    description = models.TextField(blank=True, verbose_name="Policy Description")
    project = models.ForeignKey(
        "db.Project",
        on_delete=models.CASCADE,
        related_name="approval_policies",
    )
    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="approval_policies",
    )
    issue_type = models.ForeignKey(
        "db.IssueType",
        on_delete=models.CASCADE,
        related_name="approval_policies",
        null=True,
        blank=True,
        help_text="Scope policy to specific issue type. If null, applies to all.",
    )
    approvers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ApprovalPolicyApprover",
        related_name="approval_policies",
        blank=True,
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.SEQUENTIAL,
        help_text="Sequential: approvers review one after another. Parallel: any N required.",
    )
    required_count = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of approvals required for parallel approval type.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this policy is active and can be applied.",
    )

    class Meta:
        verbose_name = "Approval Policy"
        verbose_name_plural = "Approval Policies"
        db_table = "approval_policies"
        ordering = ("-created_at",)
        unique_together = ["name", "project", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "project"],
                condition=Q(deleted_at__isnull=True),
                name="approval_policy_unique_name_project_when_deleted_at_null",
            )
        ]

    def __str__(self):
        return f"{self.name} <{self.project.name}>"

    def save(self, *args, **kwargs):
        self.workspace = self.project.workspace
        super().save(*args, **kwargs)


class ApprovalPolicyApprover(BaseModel):
    policy = models.ForeignKey(
        ApprovalPolicy,
        on_delete=models.CASCADE,
        related_name="policy_approvers",
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approver_policies",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order of approver in sequential approval flow.",
    )

    class Meta:
        verbose_name = "Approval Policy Approver"
        verbose_name_plural = "Approval Policy Approvers"
        db_table = "approval_policy_approvers"
        ordering = ("order",)
        unique_together = ["policy", "approver", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy", "approver"],
                condition=Q(deleted_at__isnull=True),
                name="approval_policy_approver_unique_policy_approver_when_deleted_at_null",
            )
        ]

    def __str__(self):
        return f"{self.policy.name} - {self.approver.email}"


class ApprovalDecision(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    policy = models.ForeignKey(
        ApprovalPolicy,
        on_delete=models.CASCADE,
        related_name="approval_decisions",
        help_text="The approval policy applied to this item.",
    )
    item_id = models.UUIDField(
        db_index=True,
        help_text="The ID of the item being approved (e.g., Issue ID).",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approval_requests",
        help_text="User who requested approval.",
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approval_responses",
        null=True,
        blank=True,
        help_text="User who approved/rejected. Null for pending.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    comment = models.TextField(blank=True, help_text="Comment from approver.")
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order in sequential approval flow.",
    )

    class Meta:
        verbose_name = "Approval Decision"
        verbose_name_plural = "Approval Decisions"
        db_table = "approval_decisions"
        ordering = ("order", "created_at")
        indexes = [
            models.Index(fields=["policy", "item_id"], name="approval_decision_policy_item_idx"),
        ]
        unique_together = ["policy", "item_id", "approver", "deleted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy", "item_id", "approver"],
                condition=Q(deleted_at__isnull=True),
                name="approval_decision_unique_policy_item_approver_when_deleted_at_null",
            )
        ]

    def __str__(self):
        return f"{self.policy.name} - {self.item_id} - {self.status}"
