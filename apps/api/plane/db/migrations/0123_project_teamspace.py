from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0122_work_item_types"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="teamspace",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="teamspace_projects",
                to="db.team",
            ),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["teamspace_id"], name="projects_teamspace_idx"),
        ),
    ]
