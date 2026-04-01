from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0127_state_agent_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="apitoken",
            name="allowed_project_ids",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
