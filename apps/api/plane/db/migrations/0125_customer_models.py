# Generated migration for customer module

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0124_teamspace_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=255)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("inactive", "Inactive"), ("archived", "Archived")],
                        default="active",
                        max_length=50,
                    ),
                ),
                ("external_source", models.CharField(blank=True, max_length=255, null=True)),
                ("external_id", models.CharField(blank=True, max_length=255, null=True)),
                ("metadata", models.JSONField(default=dict)),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workspace_customers",
                        to="db.workspace",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to="db.user",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to="db.user",
                    ),
                ),
                ("tags", models.ManyToManyField(blank=True, related_name="customer_tags", to="db.label")),
            ],
            options={
                "verbose_name": "Customer",
                "verbose_name_plural": "Customers",
                "db_table": "customers",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="CustomerContact",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(blank=True, max_length=255, null=True)),
                ("phone", models.CharField(blank=True, max_length=50, null=True)),
                ("role", models.CharField(blank=True, max_length=255, null=True)),
                ("is_primary", models.BooleanField(default=False)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="contacts", to="db.customer"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to="db.user",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to="db.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer Contact",
                "verbose_name_plural": "Customer Contacts",
                "db_table": "customer_contacts",
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddConstraint(
            model_name="customer",
            constraint=models.UniqueConstraint(
                condition=models.Q(deleted_at__isnull=True),
                fields=("email", "workspace"),
                name="customer_unique_email_workspace_when_deleted_at_null",
            ),
        ),
        migrations.AddField(
            model_name="intakeissue",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="intake_issues",
                to="db.customer",
            ),
        ),
        migrations.AddField(
            model_name="issue",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="issues",
                to="db.customer",
            ),
        ),
    ]
