from celery import shared_task
from django.db.models import Count, Q
from plane.db.models import Issue, StateGroup
from plane.utils.issue_rollup import calculate_issue_rollups


@shared_task
def recalculate_all_issue_rollups():
    all_issues = Issue.objects.filter(deleted_at__isnull=True).values_list("id", flat=True)

    total = len(all_issues)
    processed = 0

    for issue_id in all_issues:
        calculate_issue_rollups(issue_id)
        processed += 1

    return {"total": total, "processed": processed}


@shared_task
def recalculate_workspace_rollups(workspace_id):
    issues = Issue.objects.filter(
        workspace_id=workspace_id,
        deleted_at__isnull=True,
    ).values_list("id", flat=True)

    total = len(issues)
    processed = 0

    for issue_id in issues:
        calculate_issue_rollups(issue_id)
        processed += 1

    return {"workspace_id": str(workspace_id), "total": total, "processed": processed}


@shared_task
def recalculate_project_rollups(project_id):
    issues = Issue.objects.filter(
        project_id=project_id,
        deleted_at__isnull=True,
    ).values_list("id", flat=True)

    total = len(issues)
    processed = 0

    for issue_id in issues:
        calculate_issue_rollups(issue_id)
        processed += 1

    return {"project_id": str(project_id), "total": total, "processed": processed}
