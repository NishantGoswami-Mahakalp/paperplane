from django.db import migrations, models


def backfill_agent_states(apps, schema_editor):
    State = apps.get_model("db", "State")

    State.objects.filter(group="backlog").update(agent_state="backlog")
    State.objects.filter(group="completed").update(agent_state="done")
    State.objects.filter(group="cancelled").update(agent_state="cancelled")

    State.objects.filter(group="started", name="In Progress").update(agent_state="in_progress")
    State.objects.filter(group="unstarted", name="Todo").update(agent_state="ready")


def clear_agent_states(apps, schema_editor):
    State = apps.get_model("db", "State")
    State.objects.update(agent_state=None)


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0126_add_epic_to_issues"),
    ]

    operations = [
        migrations.AddField(
            model_name="state",
            name="agent_state",
            field=models.CharField(
                blank=True,
                choices=[
                    ("backlog", "Backlog"),
                    ("ready", "Ready"),
                    ("in_progress", "In Progress"),
                    ("blocked", "Blocked"),
                    ("in_review", "In Review"),
                    ("done", "Done"),
                    ("cancelled", "Cancelled"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.RunPython(backfill_agent_states, clear_agent_states),
    ]
