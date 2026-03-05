# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import RegexValidator

# Module imports
from plane.db.models.project import ProjectBaseModel

# Validators
validate_alias_format = RegexValidator(
    regex=r"^[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?$",
    message="Alias can only contain alphanumeric characters, dots, and dashes. It must start and end with an alphanumeric character.",
)

validate_domain_format = RegexValidator(
    regex=r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)+$",
    message="Invalid domain format. Domain must be a valid domain name (e.g., example.com).",
)


def validate_alias_not_reserved(value):
    reserved_aliases = {"www", "mail", "smtp", "pop", "imap", "ftp", "admin", "root", "support", "noreply", "no-reply"}
    if value.lower() in reserved_aliases:
        raise ValidationError(f"Alias '{value}' is reserved and cannot be used.")


class ProjectEmailAlias(ProjectBaseModel):
    alias = models.CharField(
        max_length=64,
        validators=[validate_alias_format, validate_alias_not_reserved],
    )
    domain = models.CharField(
        max_length=255,
        validators=[validate_domain_format],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Project Email Alias"
        verbose_name_plural = "Project Email Aliases"
        db_table = "project_email_aliases"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["alias", "domain", "project"],
                condition=models.Q(deleted_at__isnull=True),
                name="project_email_alias_unique_alias_domain_project_when_deleted_at_null",
            )
        ]

    def __str__(self):
        return f"{self.alias}@{self.domain} <{self.project.name}>"

    def clean(self):
        super().clean()
        self.alias = self.alias.lower().strip()
        self.domain = self.domain.lower().strip()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_email(self):
        return f"{self.alias}@{self.domain}"
