# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0123_project_teamspace"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="visibility",
            field=models.CharField(
                choices=[("private", "Private"), ("workspace", "Workspace")],
                default="workspace",
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="TeamspaceMember",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "role",
                    models.CharField(
                        choices=[("admin", "Admin"), ("member", "Member"), ("viewer", "Viewer")],
                        default="member",
                        max_length=20,
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teamspace_memberships",
                        to="db.user",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teamspace_members",
                        to="db.team",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%s_class_created_by" % "teamspacemember",
                        to="db.user",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%s_class_updated_by" % "teamspacemember",
                        to="db.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "Teamspace Member",
                "verbose_name_plural": "Teamspace Members",
                "db_table": "teamspace_members",
                "ordering": ("-created_at",),
                "unique_together": {("team", "member", "deleted_at")},
            },
        ),
        migrations.AddConstraint(
            model_name="teamspacemember",
            constraint=models.UniqueConstraint(
                fields=("team", "member"),
                condition=models.Q(deleted_at__isnull=True),
                name="teamspace_member_unique_team_member_when_deleted_at_null",
            ),
        ),
        migrations.CreateModel(
            name="TeamspaceProject",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teamspace_links",
                        to="db.project",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teamspace_projects",
                        to="db.team",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%s_class_created_by" % "teamspaceproject",
                        to="db.user",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%s_class_updated_by" % "teamspaceproject",
                        to="db.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "Teamspace Project",
                "verbose_name_plural": "Teamspace Projects",
                "db_table": "teamspace_projects",
                "ordering": ("-created_at",),
                "unique_together": {("team", "project", "deleted_at")},
            },
        ),
        migrations.AddConstraint(
            model_name="teamspaceproject",
            constraint=models.UniqueConstraint(
                fields=("team", "project"),
                condition=models.Q(deleted_at__isnull=True),
                name="teamspace_project_unique_team_project_when_deleted_at_null",
            ),
        ),
    ]
