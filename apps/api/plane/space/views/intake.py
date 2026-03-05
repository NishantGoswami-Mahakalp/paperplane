# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import json
import logging

# Django import
from django.utils import timezone
from django.db.models import Q, OuterRef, Func, F, Prefetch
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from .base import BaseViewSet
from plane.db.models import IntakeIssue, Issue, IssueLink, FileAsset, DeployBoard, State, Intake
from plane.db.models.intake import SourceType
from plane.db.models.state import StateGroup
from plane.app.serializers import (
    IssueSerializer,
    IntakeIssueSerializer,
    IssueCreateSerializer,
    IssueStateIntakeSerializer,
)
from plane.space.serializer.intake import IntakeFormSubmissionSerializer
from plane.space.throttles.intake import (
    IntakeSubmissionRateThrottle,
    sanitize_input,
    validate_captcha,
    log_abuse_attempt,
)
from plane.utils.issue_filters import issue_filters
from plane.bgtasks.issue_activities_task import issue_activity
from plane.db.models.intake import SourceType

logger = logging.getLogger("plane")


class IntakeIssuePublicViewSet(BaseViewSet):
    serializer_class = IntakeIssueSerializer
    model = IntakeIssue

    filterset_fields = ["status"]

    def get_queryset(self):
        project_deploy_board = DeployBoard.objects.get(
            workspace__slug=self.kwargs.get("slug"),
            project_id=self.kwargs.get("project_id"),
        )
        if project_deploy_board is not None:
            return self.filter_queryset(
                super()
                .get_queryset()
                .filter(
                    Q(snoozed_till__gte=timezone.now()) | Q(snoozed_till__isnull=True),
                    project_id=self.kwargs.get("project_id"),
                    workspace__slug=self.kwargs.get("slug"),
                    intake_id=self.kwargs.get("intake_id"),
                )
                .select_related("issue", "workspace", "project")
            )
        return IntakeIssue.objects.none()

    def list(self, request, anchor, intake_id):
        project_deploy_board = DeployBoard.objects.get(anchor=anchor, entity_name="project")
        if project_deploy_board.intake is None:
            return Response(
                {"error": "Intake is not enabled for this Project Board"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filters = issue_filters(request.query_params, "GET")
        issues = (
            Issue.objects.filter(
                issue_intake__intake_id=intake_id,
                workspace_id=project_deploy_board.workspace_id,
                project_id=project_deploy_board.project_id,
            )
            .filter(**filters)
            .annotate(bridge_id=F("issue_intake__id"))
            .select_related("workspace", "project", "state", "parent")
            .prefetch_related("assignees", "labels")
            .order_by("issue_intake__snoozed_till", "issue_intake__status")
            .annotate(
                sub_issues_count=Issue.issue_objects.filter(parent=OuterRef("id"))
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(
                link_count=IssueLink.objects.filter(issue=OuterRef("id"))
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .annotate(
                attachment_count=FileAsset.objects.filter(
                    issue_id=OuterRef("id"),
                    entity_type=FileAsset.EntityTypeContext.ISSUE_ATTACHMENT,
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            .prefetch_related(
                Prefetch(
                    "issue_intake",
                    queryset=IntakeIssue.objects.only("status", "duplicate_to", "snoozed_till", "source"),
                )
            )
        )
        issues_data = IssueStateIntakeSerializer(issues, many=True).data
        return Response(issues_data, status=status.HTTP_200_OK)

    def create(self, request, anchor, intake_id):
        project_deploy_board = DeployBoard.objects.get(anchor=anchor, entity_name="project")
        if project_deploy_board.intake is None:
            return Response(
                {"error": "Intake is not enabled for this Project Board"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.data.get("issue", {}).get("name", False):
            return Response({"error": "Name is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check for valid priority
        if request.data.get("issue", {}).get("priority", "none") not in [
            "low",
            "medium",
            "high",
            "urgent",
            "none",
        ]:
            return Response({"error": "Invalid priority"}, status=status.HTTP_400_BAD_REQUEST)

        # get the triage state
        triage_state = State.triage_objects.filter(
            project_id=project_deploy_board.project_id, workspace_id=project_deploy_board.workspace_id
        ).first()

        if not triage_state:
            triage_state = State.objects.create(
                name="Triage",
                group=StateGroup.TRIAGE.value,
                project_id=project_deploy_board.project_id,
                workspace_id=project_deploy_board.workspace_id,
                color="#4E5355",
                sequence=65000,
                default=False,
            )

        # create an issue
        issue = Issue.objects.create(
            name=request.data.get("issue", {}).get("name"),
            description_json=request.data.get("issue", {}).get("description_json", {}),
            description_html=request.data.get("issue", {}).get("description_html", "<p></p>"),
            priority=request.data.get("issue", {}).get("priority", "low"),
            project_id=project_deploy_board.project_id,
            state_id=triage_state.id,
        )

        # Create an Issue Activity
        issue_activity.delay(
            type="issue.activity.created",
            requested_data=json.dumps(request.data, cls=DjangoJSONEncoder),
            actor_id=str(request.user.id),
            issue_id=str(issue.id),
            project_id=str(project_deploy_board.project_id),
            current_instance=None,
            epoch=int(timezone.now().timestamp()),
        )
        # create an intake issue
        IntakeIssue.objects.create(
            intake_id=intake_id,
            project_id=project_deploy_board.project_id,
            issue=issue,
            source=SourceType.IN_APP,
        )

        serializer = IssueStateIntakeSerializer(issue)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, anchor, intake_id, pk):
        project_deploy_board = DeployBoard.objects.get(anchor=anchor, entity_name="project")
        if project_deploy_board.intake is None:
            return Response(
                {"error": "Intake is not enabled for this Project Board"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        intake_issue = IntakeIssue.objects.get(
            pk=pk,
            workspace_id=project_deploy_board.workspace_id,
            project_id=project_deploy_board.project_id,
            intake_id=intake_id,
        )
        # Get the project member
        if str(intake_issue.created_by_id) != str(request.user.id):
            return Response(
                {"error": "You cannot edit intake issues"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get issue data
        issue_data = request.data.pop("issue", False)

        issue = Issue.objects.get(
            pk=intake_issue.issue_id,
            workspace_id=project_deploy_board.workspace_id,
            project_id=project_deploy_board.project_id,
        )
        # viewers and guests since only viewers and guests
        issue_data = {
            "name": issue_data.get("name", issue.name),
            "description_html": issue_data.get("description_html", issue.description_html),
            "description_json": issue_data.get("description_json", issue.description_json),
        }

        issue_serializer = IssueCreateSerializer(
            issue,
            data=issue_data,
            partial=True,
            context={"project_id": project_deploy_board.project_id, "allow_triage_state": True},
        )

        if issue_serializer.is_valid():
            current_instance = issue
            # Log all the updates
            requested_data = json.dumps(issue_data, cls=DjangoJSONEncoder)
            if issue is not None:
                issue_activity.delay(
                    type="issue.activity.updated",
                    requested_data=requested_data,
                    actor_id=str(request.user.id),
                    issue_id=str(issue.id),
                    project_id=str(project_deploy_board.project_id),
                    current_instance=json.dumps(IssueSerializer(current_instance).data, cls=DjangoJSONEncoder),
                    epoch=int(timezone.now().timestamp()),
                )
            issue_serializer.save()
            return Response(issue_serializer.data, status=status.HTTP_200_OK)
        return Response(issue_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, anchor, intake_id, pk):
        project_deploy_board = DeployBoard.objects.get(anchor=anchor, entity_name="project")
        if project_deploy_board.intake is None:
            return Response(
                {"error": "Intake is not enabled for this Project Board"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        intake_issue = IntakeIssue.objects.get(
            pk=pk,
            workspace_id=project_deploy_board.workspace_id,
            project_id=project_deploy_board.project_id,
            intake_id=intake_id,
        )
        issue = Issue.objects.get(
            pk=intake_issue.issue_id,
            workspace_id=project_deploy_board.workspace_id,
            project_id=project_deploy_board.project_id,
        )
        serializer = IssueStateIntakeSerializer(issue)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, anchor, intake_id, pk):
        project_deploy_board = DeployBoard.objects.get(anchor=anchor, entity_name="project")
        if project_deploy_board.intake is None:
            return Response(
                {"error": "Intake is not enabled for this Project Board"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        intake_issue = IntakeIssue.objects.get(
            pk=pk,
            workspace_id=project_deploy_board.workspace_id,
            project_id=project_deploy_board.project_id,
            intake_id=intake_id,
        )

        if str(intake_issue.created_by_id) != str(request.user.id):
            return Response(
                {"error": "You cannot delete intake issue"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        intake_issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IntakeFormSubmitEndpoint(BaseViewSet):
    """
    Public endpoint for submitting intake form data.
    Includes rate limiting, captcha validation, and input sanitization.
    """

    throttle_classes = [IntakeSubmissionRateThrottle]

    # Disable authentication for public endpoint
    permission_classes = []

    def create(self, request, anchor, form_id):
        """
        Submit intake form data.

        POST /anchor/{anchor}/intake/{form_id}/submit/

        Request body:
        {
            "fields": {
                "field_name": "value",
                ...
            },
            "captcha_token": "optional_captcha_token"
        }
        """
        # Get the project deploy board
        try:
            project_deploy_board = DeployBoard.objects.get(anchor=anchor, entity_name="project")
        except DeployBoard.DoesNotExist:
            log_abuse_attempt(request, form_id, "invalid_anchor", {"anchor": anchor})
            return Response(
                {"error": "Invalid anchor"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if intake is enabled
        if project_deploy_board.intake is None:
            log_abuse_attempt(request, form_id, "intake_disabled", {"anchor": anchor})
            return Response(
                {"error": "Intake is not enabled for this Project Board"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate captcha/token
        captcha_token = request.data.get("captcha_token")
        is_captcha_valid, captcha_error = validate_captcha(request, captcha_token)

        if not is_captcha_valid:
            log_abuse_attempt(request, form_id, "invalid_captcha", {"error": captcha_error})
            return Response(
                {"error": captcha_error or "Captcha validation failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate the submission data
        serializer = IntakeFormSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            log_abuse_attempt(request, form_id, "invalid_submission", {"errors": serializer.errors})
            return Response(
                {"error": "Invalid submission data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fields = serializer.validated_data.get("fields", {})

        # Get the intake for this form
        from plane.db.models import Intake

        try:
            intake = Intake.objects.get(
                pk=form_id,
                project_id=project_deploy_board.project_id,
                workspace_id=project_deploy_board.workspace_id,
                is_active=True,
            )
        except Intake.DoesNotExist:
            log_abuse_attempt(request, form_id, "invalid_form_id", {"form_id": str(form_id)})
            return Response(
                {"error": "Form not found or inactive"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Sanitize input fields
        sanitized_fields = {}
        for field_name, value in fields.items():
            # Determine field type (default to text if not specified)
            field_type = "text"
            if intake.field_config_json:
                for field_config in intake.field_config_json:
                    if field_config.get("id") == field_name or field_config.get("name") == field_name:
                        field_type = field_config.get("type", "text")
                        break

            sanitized_value = sanitize_input(value, field_type)
            if sanitized_value is not None or value == "":
                sanitized_fields[field_name] = sanitized_value

        # Map fields to issue properties using field mapping
        # (This will use the field_config_json when available)
        issue_data = self._map_fields_to_issue_properties(sanitized_fields, intake)

        # Validate required name field
        if not issue_data.get("name"):
            return Response(
                {"error": "Name field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create triage state
        triage_state = State.triage_objects.filter(
            project_id=project_deploy_board.project_id, workspace_id=project_deploy_board.workspace_id
        ).first()

        if not triage_state:
            triage_state = State.objects.create(
                name="Triage",
                group=StateGroup.TRIAGE.value,
                project_id=project_deploy_board.project_id,
                workspace_id=project_deploy_board.workspace_id,
                color="#4E5355",
                sequence=65000,
                default=False,
            )

        issue_data["state_id"] = triage_state.id
        issue_data["project_id"] = project_deploy_board.project_id
        issue_data["workspace_id"] = project_deploy_board.workspace_id

        # Create the issue
        issue = Issue.objects.create(**issue_data)

        # Log the creation
        logger.info(
            "Intake form submitted",
            extra={
                "issue_id": str(issue.id),
                "form_id": str(form_id),
                "anchor": anchor,
                "project_id": str(project_deploy_board.project_id),
            },
        )

        # Create intake issue record
        IntakeIssue.objects.create(
            intake_id=intake.id,
            project_id=project_deploy_board.project_id,
            issue=issue,
            source=SourceType.PUBLIC_FORM,
        )

        # Return the created issue
        issue_serializer = IssueStateIntakeSerializer(issue)
        return Response(
            {
                "success": True,
                "message": "Form submitted successfully",
                "issue": issue_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def _map_fields_to_issue_properties(self, fields, intake):
        """
        Map form fields to issue properties based on field configuration.

        This uses the field_config_json from the intake to map fields
        to issue properties like name, description, priority, etc.
        """
        issue_data = {}

        # Get field configuration from intake
        field_config = intake.field_config_json if hasattr(intake, "field_config_json") else []

        if not field_config:
            # Fallback: use simple field mapping
            # Try to find common fields
            if "name" in fields:
                issue_data["name"] = fields["name"]
            elif "title" in fields:
                issue_data["name"] = fields["title"]
            elif "subject" in fields:
                issue_data["name"] = fields["subject"]

            if "description" in fields:
                issue_data["description_html"] = f"<p>{fields['description']}</p>"
                issue_data["description_json"] = {
                    "type": "doc",
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": fields["description"]}]}],
                }

            if "priority" in fields:
                priority = fields["priority"].lower()
                if priority in ["low", "medium", "high", "urgent"]:
                    issue_data["priority"] = priority
                else:
                    issue_data["priority"] = "none"

            return issue_data

        # Use field configuration for mapping
        for field in field_config:
            field_id = field.get("id")
            field_name = field.get("name")
            target_property = field.get("target_property")

            # Get the value from submitted fields
            value = fields.get(field_id) or fields.get(field_name)

            if value is None:
                # Check if field has a default value
                value = field.get("default_value")

            if value is None and field.get("required"):
                # Skip if required field has no value
                continue

            # Map to target property
            if target_property == "name" and value:
                issue_data["name"] = str(value)
            elif target_property == "description" and value:
                issue_data["description_html"] = f"<p>{value}</p>"
                issue_data["description_json"] = {
                    "type": "doc",
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": str(value)}]}],
                }
            elif target_property == "priority" and value:
                priority = str(value).lower()
                if priority in ["low", "medium", "high", "urgent"]:
                    issue_data["priority"] = priority
                else:
                    issue_data["priority"] = "none"

        # If no name was mapped, try to find it in fields
        if "name" not in issue_data:
            for key, value in fields.items():
                if key.lower() in ["name", "title", "subject", "summary"]:
                    issue_data["name"] = str(value)
                    break

        return issue_data


class IntakeFormPublicConfigEndpoint(BaseViewSet):
    """
    Public endpoint to get intake form configuration.
    Returns the form fields that can be submitted.
    """

    permission_classes = []

    def retrieve(self, request, anchor, form_id):
        """
        Get intake form configuration.

        GET /anchor/{anchor}/intake/{form_id}/config/
        """
        try:
            project_deploy_board = DeployBoard.objects.get(anchor=anchor, entity_name="project")
        except DeployBoard.DoesNotExist:
            return Response(
                {"error": "Invalid anchor"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if project_deploy_board.intake is None:
            return Response(
                {"error": "Intake is not enabled for this Project Board"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from plane.db.models import Intake

        try:
            intake = Intake.objects.get(
                pk=form_id,
                project_id=project_deploy_board.project_id,
                workspace_id=project_deploy_board.workspace_id,
                is_active=True,
            )
        except Intake.DoesNotExist:
            return Response(
                {"error": "Form not found or inactive"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Return form configuration
        return Response(
            {
                "id": str(intake.id),
                "name": intake.name,
                "description": intake.description,
                "fields": intake.field_config_json if hasattr(intake, "field_config_json") else [],
            },
            status=status.HTTP_200_OK,
        )
