from django.db.models import Count, Q
from plane.db.models import Issue, StateGroup


def calculate_issue_rollups(issue_id):
    try:
        issue = Issue.objects.get(pk=issue_id)
    except Issue.DoesNotExist:
        return

    child_issues = Issue.objects.filter(parent=issue, deleted_at__isnull=True)

    total_children = child_issues.count()
    completed_children = child_issues.filter(
        state__group__in=[StateGroup.COMPLETED.value, StateGroup.CANCELLED.value]
    ).count()

    progress = 0.0
    if total_children > 0:
        progress = round((completed_children / total_children) * 100, 2)

    Issue.objects.filter(pk=issue_id).update(
        child_issues_count=total_children,
        completed_child_issues_count=completed_children,
        child_issues_progress=progress,
    )

    return {
        "issue_id": str(issue_id),
        "child_issues_count": total_children,
        "completed_child_issues_count": completed_children,
        "child_issues_progress": progress,
    }


def update_ancestor_rollups(issue_id):
    issue = Issue.objects.filter(pk=issue_id).first()
    if not issue:
        return

    ancestor_ids = []
    current = issue.parent
    while current is not None:
        ancestor_ids.append(current.id)
        current = current.parent

    for ancestor_id in ancestor_ids:
        calculate_issue_rollups(ancestor_id)
