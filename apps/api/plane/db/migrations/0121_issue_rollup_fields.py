from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0120_issueview_archived_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="child_issues_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="issue",
            name="completed_child_issues_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="issue",
            name="child_issues_progress",
            field=models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]),
        ),
    ]
