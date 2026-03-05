# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.db import models

# Module imports
from plane.db.models import BaseModel
from plane.db.models import Label


class CustomerStatus(models.TextChoices):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Customer(BaseModel):
    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="workspace_customers",
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    company = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=50,
        choices=CustomerStatus.choices,
        default=CustomerStatus.ACTIVE,
    )
    external_source = models.CharField(max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict)
    tags = models.ManyToManyField(Label, blank=True, related_name="customer_tags")

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        db_table = "customers"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["email", "workspace"],
                condition=models.Q(deleted_at__isnull=True),
                name="customer_unique_email_workspace_when_deleted_at_null",
            )
        ]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class CustomerContact(BaseModel):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Customer Contact"
        verbose_name_plural = "Customer Contacts"
        db_table = "customer_contacts"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} <{self.customer.name}>"


class CustomerComment(BaseModel):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    comment = models.TextField()

    class Meta:
        verbose_name = "Customer Comment"
        verbose_name_plural = "Customer Comments"
        db_table = "customer_comments"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Comment on {self.customer.name}"
