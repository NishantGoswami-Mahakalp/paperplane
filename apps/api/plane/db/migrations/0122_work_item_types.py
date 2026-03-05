from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0121_issue_rollup_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkItemType",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default="8f3c9f4a-6b5c-4d8e-9f1a-2c3b4e5f6a7b",
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "work_item_type",
                    models.CharField(
                        choices=[("task", "Task"), ("bug", "Bug"), ("story", "Story")],
                        default="task",
                        max_length=50,
                    ),
                ),
                ("logo_props", models.JSONField(default=dict)),
                ("is_epic", models.BooleanField(default=False)),
                ("is_default", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("schema_version", models.PositiveIntegerField(default=1)),
                ("external_source", models.CharField(blank=True, max_length=255, null=True)),
                ("external_id", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to="db.user",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to="db.user",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="work_item_types",
                        to="db.workspace",
                    ),
                ),
            ],
            options={
                "verbose_name": "Work Item Type",
                "verbose_name_plural": "Work Item Types",
                "db_table": "work_item_types",
            },
        ),
        migrations.CreateModel(
            name="FieldDefinition",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default="8f3c9f4a-6b5c-4d8e-9f1a-2c3b4e5f6a7c",
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "field_type",
                    models.CharField(
                        choices=[
                            ("text", "Text"),
                            ("number", "Number"),
                            ("select", "Select"),
                            ("multiselect", "MultiSelect"),
                            ("date", "Date"),
                            ("email", "Email"),
                            ("url", "URL"),
                            ("checkbox", "Checkbox"),
                            ("user", "User"),
                            ("users", "Users"),
                            ("relation", "Relation"),
                            ("rich_text", "Rich Text"),
                        ],
                        max_length=50,
                    ),
                ),
                ("is_required", models.BooleanField(default=False)),
                ("position", models.PositiveIntegerField(default=0)),
                ("validation_rules", models.JSONField(default=dict)),
                ("options", models.JSONField(default=list)),
                ("external_source", models.CharField(blank=True, max_length=255, null=True)),
                ("external_id", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to="db.user",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to="db.user",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="field_definitions",
                        to="db.workspace",
                    ),
                ),
            ],
            options={
                "verbose_name": "Field Definition",
                "verbose_name_plural": "Field Definitions",
                "db_table": "field_definitions",
                "ordering": ("position",),
            },
        ),
        migrations.CreateModel(
            name="ProjectWorkItemType",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default="8f3c9f4a-6b5c-4d8e-9f1a-2c3b4e5f6a7d",
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("position", models.PositiveIntegerField(default=0)),
                ("is_default", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to="db.user",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to="db.user",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="project_%(class)s",
                        to="db.project",
                    ),
                ),
                (
                    "work_item_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="project_work_item_types",
                        to="db.workitemtype",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workspace_%(class)s",
                        to="db.workspace",
                    ),
                ),
            ],
            options={
                "verbose_name": "Project Work Item Type",
                "verbose_name_plural": "Project Work Item Types",
                "db_table": "project_work_item_types",
                "ordering": ("position",),
                "unique_together": {("project", "work_item_type", "deleted_at")},
            },
        ),
        migrations.CreateModel(
            name="WorkItemTypeField",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default="8f3c9f4a-6b5c-4d8e-9f1a-2c3b4e5f6a7e",
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("is_required", models.BooleanField(default=False)),
                ("position", models.PositiveIntegerField(default=0)),
                ("validations", models.JSONField(default=dict)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to="db.user",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to="db.user",
                    ),
                ),
                (
                    "field_definition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="work_item_type_fields",
                        to="db.fielddefinition",
                    ),
                ),
                (
                    "work_item_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="work_item_type_fields",
                        to="db.workitemtype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Work Item Type Field",
                "verbose_name_plural": "Work Item Type Fields",
                "db_table": "work_item_type_fields",
                "ordering": ("position",),
                "unique_together": {("work_item_type", "field_definition", "deleted_at")},
            },
        ),
        migrations.AddConstraint(
            model_name="workitemtype",
            constraint=models.UniqueConstraint(
                fields=("workspace", "name"),
                condition=models.Q(deleted_at__isnull=True),
                name="work_item_type_unique_name_workspace_when_deleted_at_null",
            ),
        ),
        migrations.AddConstraint(
            model_name="fielddefinition",
            constraint=models.UniqueConstraint(
                fields=("workspace", "name"),
                condition=models.Q(deleted_at__isnull=True),
                name="field_definition_unique_name_workspace_when_deleted_at_null",
            ),
        ),
        migrations.AddConstraint(
            model_name="projectworkitemtype",
            constraint=models.UniqueConstraint(
                fields=("project", "work_item_type"),
                condition=models.Q(deleted_at__isnull=True),
                name="project_work_item_type_unique_project_work_item_type_when_deleted_at_null",
            ),
        ),
        migrations.AddConstraint(
            model_name="workitemtypefield",
            constraint=models.UniqueConstraint(
                fields=("work_item_type", "field_definition"),
                condition=models.Q(deleted_at__isnull=True),
                name="work_item_type_field_unique_work_item_type_field_when_deleted_at_null",
            ),
        ),
    ]
