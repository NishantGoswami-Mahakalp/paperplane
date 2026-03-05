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
            field=models.FloatField(
                default=0.0, validators=[models.MinValueValidator(0.0), models.MaxValueValidator(100.0)]
            ),
        ),
    ]
