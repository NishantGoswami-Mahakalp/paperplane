import uuid

from rest_framework import status
from rest_framework.response import Response

from plane.app.permissions import ProjectEntityPermission
from plane.db.models import Issue, IssueRelation
from plane.utils.issue_relation_mapper import get_actual_relation

from .agent import _build_issue_contexts
from .base import BaseAPIView

ALLOWED_RELATION_TYPES = {
    "blocked_by",
    "blocking",
    "relates_to",
    "duplicate",
    "start_before",
    "start_after",
    "finish_before",
    "finish_after",
    "implemented_by",
    "implements",
}


class IssueRelationListCreateAPIEndpoint(BaseAPIView):
    permission_classes = [ProjectEntityPermission]
    use_read_replica = False

    def get_issue(self):
        return Issue.issue_objects.get(
            workspace__slug=self.kwargs.get("slug"),
            project_id=self.kwargs.get("project_id"),
            pk=self.kwargs.get("issue_id"),
        )

    def get(self, request, slug, project_id, issue_id):
        issue = self.get_issue()
        context = _build_issue_contexts([issue])

        return Response(
            {
                "work_item_id": issue.id,
                "relations": context[issue.id]["relations"],
                "open_blockers": context[issue.id]["open_blockers"],
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, slug, project_id, issue_id):
        issue = self.get_issue()
        relation_type = request.data.get("relation_type")
        related_issue_ids = request.data.get("issues", [])

        if relation_type not in ALLOWED_RELATION_TYPES:
            return Response(
                {"error": "relation_type must be one of the supported relation values"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(related_issue_ids, list) or not related_issue_ids:
            return Response({"error": "issues must be a non-empty list"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            normalized_issue_ids = [uuid.UUID(str(related_issue_id)) for related_issue_id in related_issue_ids]
        except ValueError:
            return Response({"error": "issues must contain valid UUIDs"}, status=status.HTTP_400_BAD_REQUEST)

        if uuid.UUID(str(issue_id)) in normalized_issue_ids:
            return Response({"error": "A work item cannot relate to itself"}, status=status.HTTP_400_BAD_REQUEST)

        related_issues = list(
            Issue.issue_objects.filter(
                workspace__slug=slug,
                project_id=project_id,
                pk__in=normalized_issue_ids,
            )
        )

        if len(related_issues) != len(normalized_issue_ids):
            return Response(
                {"error": "All related issues must belong to the same project"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stored_relation_type = get_actual_relation(relation_type)
        created_relations = []
        for related_issue in related_issues:
            if relation_type in {"blocking", "start_after", "finish_after"}:
                issue_pk = related_issue.id
                related_issue_pk = issue_id
            else:
                issue_pk = issue_id
                related_issue_pk = related_issue.id

            relation, _ = IssueRelation.objects.get_or_create(
                issue_id=issue_pk,
                related_issue_id=related_issue_pk,
                defaults={
                    "relation_type": stored_relation_type,
                    "project_id": project_id,
                    "workspace_id": issue.workspace_id,
                    "created_by": request.user,
                    "updated_by": request.user,
                },
            )

            if relation.relation_type != stored_relation_type:
                relation.relation_type = stored_relation_type
                relation.updated_by = request.user
                relation.save(update_fields=["relation_type", "updated_by"])

            created_relations.append(relation)

        context = _build_issue_contexts([issue])
        return Response(
            {
                "work_item_id": issue.id,
                "created": len(created_relations),
                "relations": context[issue.id]["relations"],
                "open_blockers": context[issue.id]["open_blockers"],
            },
            status=status.HTTP_201_CREATED,
        )
