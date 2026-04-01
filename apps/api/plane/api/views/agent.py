# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from datetime import timezone as datetime_timezone

from collections import defaultdict
from uuid import UUID

from django.db.models import Exists, OuterRef, Q
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response

from plane.api.agent_config import SEVA_DESCRIPTION_TEMPLATE, get_seva_configuration, get_seva_issue_types
from plane.api.serializers import ProjectLiteSerializer, StateSerializer, UserLiteSerializer
from plane.app.permissions import ProjectEntityPermission
from plane.db.models import (
    Issue,
    IssueComment,
    IssueHierarchyLink,
    IssueType,
    IssueRelation,
    Label,
    Project,
    State,
    StateAgentType,
    StateGroup,
    User,
)
from plane.db.models.issue import IssueRelationChoices

from .base import BaseAPIView

RESOLVED_AGENT_STATES = {
    StateAgentType.DONE.value,
    StateAgentType.CANCELLED.value,
}
RESOLVED_STATE_GROUPS = {
    StateGroup.COMPLETED.value,
    StateGroup.CANCELLED.value,
}


def _serialize_state(state):
    if state is None:
        return None

    return {
        "id": state.id,
        "name": state.name,
        "group": state.group,
        "agent_state": state.agent_state,
        "color": state.color,
        "default": state.default,
    }


def _serialize_label(label):
    return {
        "id": label.id,
        "name": label.name,
        "description": label.description,
        "color": label.color,
        "parent": label.parent_id,
    }


def _serialize_issue_type(issue):
    if issue.type is None:
        return None

    return {
        "id": issue.type_id,
        "name": issue.type.name,
        "description": issue.type.description,
        "is_default": issue.type.is_default,
    }


def _serialize_issue_reference(issue):
    return {
        "id": issue.id,
        "sequence_id": issue.sequence_id,
        "title": issue.name,
        "priority": issue.priority,
        "project_id": issue.project_id,
        "state": _serialize_state(issue.state),
    }


def _is_resolved_issue(issue):
    if issue.state is None:
        return False

    return issue.state.agent_state in RESOLVED_AGENT_STATES or issue.state.group in RESOLVED_STATE_GROUPS


def _build_issue_contexts(issues):
    if not issues:
        return {}

    issue_ids = [issue.id for issue in issues]
    relation_map = {issue_id: defaultdict(list) for issue_id in issue_ids}
    hierarchy_map = {issue_id: {"parents": [], "children": []} for issue_id in issue_ids}

    def add_hierarchy_link(issue_id, direction, related_issue):
        if issue_id not in hierarchy_map:
            return

        if all(existing_issue.id != related_issue.id for existing_issue in hierarchy_map[issue_id][direction]):
            hierarchy_map[issue_id][direction].append(related_issue)

    relations = (
        IssueRelation.objects.filter(Q(issue_id__in=issue_ids) | Q(related_issue_id__in=issue_ids))
        .filter(project_id=issues[0].project_id, deleted_at__isnull=True)
        .select_related("issue__state", "related_issue__state")
        .order_by("created_at")
    )

    for relation in relations:
        if relation.issue_id in relation_map:
            relation_map[relation.issue_id][relation.relation_type].append(relation.related_issue)

        if relation.related_issue_id in relation_map:
            reverse_relation = IssueRelationChoices._REVERSE_MAPPING.get(relation.relation_type, relation.relation_type)
            relation_map[relation.related_issue_id][reverse_relation].append(relation.issue)

    hierarchy_links = (
        IssueHierarchyLink.objects.filter(Q(parent_issue_id__in=issue_ids) | Q(child_issue_id__in=issue_ids))
        .filter(project_id=issues[0].project_id, deleted_at__isnull=True)
        .select_related("parent_issue__state", "child_issue__state")
        .order_by("created_at")
    )

    for link in hierarchy_links:
        if link.parent_issue_id in hierarchy_map:
            add_hierarchy_link(link.parent_issue_id, "children", link.child_issue)

        if link.child_issue_id in hierarchy_map:
            add_hierarchy_link(link.child_issue_id, "parents", link.parent_issue)

    direct_hierarchy_issues = list(
        Issue.issue_objects.filter(
            Q(parent_id__in=issue_ids) | Q(id__in=[issue.parent_id for issue in issues if issue.parent_id])
        )
        .select_related("state", "parent")
        .order_by("created_at")
    )

    for direct_hierarchy_issue in direct_hierarchy_issues:
        if direct_hierarchy_issue.parent_id:
            add_hierarchy_link(direct_hierarchy_issue.id, "parents", direct_hierarchy_issue.parent)
            add_hierarchy_link(direct_hierarchy_issue.parent_id, "children", direct_hierarchy_issue)

    contexts = {}

    for issue in issues:
        blocked_by = relation_map[issue.id].get(IssueRelationChoices.BLOCKED_BY.value, [])
        open_blockers = [blocking_issue for blocking_issue in blocked_by if not _is_resolved_issue(blocking_issue)]

        contexts[issue.id] = {
            "relations": {
                relation_type: [_serialize_issue_reference(related_issue) for related_issue in related_issues]
                for relation_type, related_issues in relation_map[issue.id].items()
                if related_issues
            },
            "hierarchy": {
                "parents": [
                    _serialize_issue_reference(parent_issue) for parent_issue in hierarchy_map[issue.id]["parents"]
                ],
                "children": [
                    _serialize_issue_reference(child_issue) for child_issue in hierarchy_map[issue.id]["children"]
                ],
            },
            "open_blockers": [_serialize_issue_reference(blocking_issue) for blocking_issue in open_blockers],
            "is_actionable": issue.state is not None
            and issue.state.agent_state == StateAgentType.READY.value
            and not open_blockers,
        }

    return contexts


def _serialize_agent_issue(issue, context):
    return {
        "id": issue.id,
        "sequence_id": issue.sequence_id,
        "title": issue.name,
        "description": issue.description_stripped or "",
        "description_html": issue.description_html,
        "state": _serialize_state(issue.state),
        "priority": issue.priority,
        "project": ProjectLiteSerializer(issue.project).data,
        "type": _serialize_issue_type(issue),
        "assignees": UserLiteSerializer(issue.assignees.all(), many=True).data,
        "labels": [_serialize_label(label) for label in issue.labels.all()],
        "parent": _serialize_issue_reference(issue.parent) if issue.parent else None,
        "start_date": issue.start_date,
        "target_date": issue.target_date,
        "completed_at": issue.completed_at,
        "created_at": issue.created_at,
        "updated_at": issue.updated_at,
        "relations": context["relations"],
        "hierarchy": context["hierarchy"],
        "open_blockers": context["open_blockers"],
        "is_actionable": context["is_actionable"],
    }


class ProjectAgentContextAPIEndpoint(BaseAPIView):
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_project(self):
        return Project.objects.get(workspace__slug=self.kwargs.get("slug"), pk=self.kwargs.get("project_id"))

    def get(self, request, slug, project_id):
        project = self.get_project()

        states = State.objects.filter(project_id=project_id, workspace__slug=slug, deleted_at__isnull=True).order_by(
            "sequence"
        )
        labels = Label.objects.filter(project_id=project_id, workspace__slug=slug, deleted_at__isnull=True).order_by(
            "name"
        )
        members = (
            User.objects.filter(member_project__project_id=project_id, member_project__is_active=True)
            .distinct()
            .order_by("first_name", "last_name", "email")
        )
        issue_types = get_seva_issue_types(project)
        serialized_issue_types = [_serialize_issue_type_reference(issue_type) for issue_type in issue_types]

        return Response(
            {
                "project": ProjectLiteSerializer(project).data,
                "states": StateSerializer(states, many=True).data,
                "labels": [_serialize_label(label) for label in labels],
                "members": UserLiteSerializer(members, many=True).data,
                "issue_types": serialized_issue_types,
                "work_item_types": serialized_issue_types,
                "description_template": SEVA_DESCRIPTION_TEMPLATE,
                "seva_configuration": get_seva_configuration(project),
            },
            status=status.HTTP_200_OK,
        )


class ProjectReadyWorkItemsAPIEndpoint(BaseAPIView):
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        unresolved_blockers = (
            IssueRelation.objects.filter(
                issue_id=OuterRef("id"),
                relation_type=IssueRelationChoices.BLOCKED_BY.value,
                deleted_at__isnull=True,
            )
            .exclude(related_issue__state__agent_state__in=RESOLVED_AGENT_STATES)
            .exclude(related_issue__state__group__in=RESOLVED_STATE_GROUPS)
        )

        return (
            Issue.issue_objects.filter(
                project_id=self.kwargs.get("project_id"), workspace__slug=self.kwargs.get("slug")
            )
            .filter(state__agent_state=StateAgentType.READY.value)
            .select_related("project", "state", "parent", "type")
            .prefetch_related("assignees", "labels")
            .annotate(has_unresolved_blockers=Exists(unresolved_blockers))
            .order_by("-created_at")
        )

    def serialize_ready_results(self, issues):
        contexts = _build_issue_contexts(list(issues))
        return [_serialize_agent_issue(issue, contexts[issue.id]) for issue in issues]

    def get(self, request, slug, project_id):
        actionable_only = request.GET.get("actionable", "true").lower() != "false"
        queryset = self.get_queryset()

        if actionable_only:
            queryset = queryset.filter(has_unresolved_blockers=False)

        project = Project.objects.get(workspace__slug=slug, pk=project_id)

        return self.paginate(
            request=request,
            queryset=queryset,
            extra_stats={"project": ProjectLiteSerializer(project).data},
            on_results=lambda issues: self.serialize_ready_results(issues),
        )


class WorkItemAgentContextAPIEndpoint(BaseAPIView):
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return (
            Issue.issue_objects.filter(
                project_id=self.kwargs.get("project_id"), workspace__slug=self.kwargs.get("slug")
            )
            .select_related("project", "state", "parent", "type")
            .prefetch_related("assignees", "labels")
        )

    def get(self, request, slug, project_id, issue_id):
        issue = self.get_queryset().get(pk=issue_id)
        context = _build_issue_contexts([issue])

        return Response(
            {
                "project": ProjectLiteSerializer(issue.project).data,
                "work_item": _serialize_agent_issue(issue, context[issue.id]),
            },
            status=status.HTTP_200_OK,
        )


def _serialize_issue_type_reference(issue_type: IssueType):
    return {
        "id": issue_type.id,
        "name": issue_type.name,
        "description": issue_type.description,
        "is_default": issue_type.is_default,
    }


def _parse_agent_cursor(raw_cursor):
    if not raw_cursor:
        return None, None

    timestamp_raw, separator, issue_id = raw_cursor.partition("::")
    timestamp_raw = timestamp_raw.strip()
    if "T" in timestamp_raw and " " in timestamp_raw:
        timestamp_raw = timestamp_raw.replace(" ", "+")

    timestamp = parse_datetime(timestamp_raw)
    if timestamp is None:
        raise ValueError("Invalid cursor timestamp")

    if not separator:
        return timestamp, None

    if not issue_id:
        raise ValueError("Invalid cursor issue id")

    try:
        UUID(issue_id)
    except ValueError as exc:
        raise ValueError("Invalid cursor issue id") from exc

    return timestamp, issue_id


def _format_agent_cursor(updated_at, entity_id):
    if updated_at.tzinfo is not None:
        updated_at = updated_at.astimezone(datetime_timezone.utc)

    return f"{updated_at.isoformat().replace('+00:00', 'Z')}::{entity_id}"


class ProjectAgentUpdatesAPIEndpoint(BaseAPIView):
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return (
            Issue.issue_objects.filter(
                project_id=self.kwargs.get("project_id"), workspace__slug=self.kwargs.get("slug")
            )
            .select_related("project", "state", "parent", "type")
            .prefetch_related("assignees", "labels")
            .order_by("updated_at", "id")
        )

    def get(self, request, slug, project_id):
        try:
            cursor_timestamp, cursor_issue_id = _parse_agent_cursor(request.GET.get("cursor"))
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            limit = min(max(int(request.GET.get("limit", 100)), 1), 200)
        except ValueError:
            return Response({"error": "limit must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        if cursor_timestamp is not None:
            cursor_filter = Q(updated_at__gt=cursor_timestamp)
            if cursor_issue_id is not None:
                cursor_filter |= Q(updated_at=cursor_timestamp, id__gt=cursor_issue_id)
            queryset = queryset.filter(cursor_filter)

        issues = list(queryset[:limit])
        contexts = _build_issue_contexts(issues)
        next_cursor = None
        if issues:
            last_issue = issues[-1]
            next_cursor = _format_agent_cursor(last_issue.updated_at, last_issue.id)

        project = Project.objects.get(workspace__slug=slug, pk=project_id)

        return Response(
            {
                "project": ProjectLiteSerializer(project).data,
                "polling": {
                    "cursor": request.GET.get("cursor"),
                    "next_cursor": next_cursor,
                    "limit": limit,
                    "strategy": "updated_at_then_id",
                },
                "results": [_serialize_agent_issue(issue, contexts[issue.id]) for issue in issues],
            },
            status=status.HTTP_200_OK,
        )


def _serialize_comment_update(issue_comment):
    return {
        "id": issue_comment.id,
        "issue_id": issue_comment.issue_id,
        "issue_sequence_id": issue_comment.issue.sequence_id,
        "issue_title": issue_comment.issue.name,
        "issue_state": _serialize_state(issue_comment.issue.state),
        "actor": UserLiteSerializer(issue_comment.actor).data if issue_comment.actor else None,
        "comment": issue_comment.comment_stripped,
        "comment_html": issue_comment.comment_html,
        "created_at": issue_comment.created_at,
        "updated_at": issue_comment.updated_at,
        "edited_at": issue_comment.edited_at,
    }


class ProjectAgentCommentUpdatesAPIEndpoint(BaseAPIView):
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return (
            IssueComment.objects.filter(
                project_id=self.kwargs.get("project_id"), workspace__slug=self.kwargs.get("slug")
            )
            .select_related("issue", "issue__state", "actor")
            .order_by("updated_at", "id")
        )

    def get(self, request, slug, project_id):
        try:
            cursor_timestamp, cursor_comment_id = _parse_agent_cursor(request.GET.get("cursor"))
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            limit = min(max(int(request.GET.get("limit", 100)), 1), 200)
        except ValueError:
            return Response({"error": "limit must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        if cursor_timestamp is not None:
            cursor_filter = Q(updated_at__gt=cursor_timestamp)
            if cursor_comment_id is not None:
                cursor_filter |= Q(updated_at=cursor_timestamp, id__gt=cursor_comment_id)
            queryset = queryset.filter(cursor_filter)

        comments = list(queryset[:limit])
        next_cursor = None
        if comments:
            last_comment = comments[-1]
            next_cursor = _format_agent_cursor(last_comment.updated_at, last_comment.id)

        project = Project.objects.get(workspace__slug=slug, pk=project_id)

        return Response(
            {
                "project": ProjectLiteSerializer(project).data,
                "polling": {
                    "cursor": request.GET.get("cursor"),
                    "next_cursor": next_cursor,
                    "limit": limit,
                    "strategy": "updated_at_then_id",
                },
                "results": [_serialize_comment_update(comment) for comment in comments],
            },
            status=status.HTTP_200_OK,
        )
