# Generated manually to fix missing epic_id column on fresh database

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0125_customer_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="epic_id",
            field=models.UUIDField(null=True, blank=True),
        ),
    ]
