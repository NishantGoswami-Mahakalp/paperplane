# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from __future__ import annotations

# Python imports
import hashlib
import logging
from dataclasses import dataclass
from typing import Optional

# Django imports
from django.utils import timezone
from django.db import transaction

# Third party imports
from rest_framework import status

logger = logging.getLogger("plane.api")

DEDUP_WINDOW_HOURS = 24


@dataclass
class EmailIngestionResult:
    success: bool
    work_item_id: Optional[str] = None
    is_duplicate: bool = False
    message: str = ""
    status_code: int = status.HTTP_200_OK


class EmailIngestionService:
    """
    Service for ingesting emails and creating work items.
    Handles parsing, deduplication, and work item creation.
    """

    def __init__(self):
        from plane.db.models import (  # noqa: E402
            Intake,
            IntakeIssue,
            IntakeIssueStatus,
            Issue,
            Project,
            ProjectEmailAlias,
            ReceivedEmail,
            State,
            StateGroup,
            Workspace,
        )
        from plane.utils.email_parser import EmailParser, ParsedEmail  # noqa: E402

        self.parser = EmailParser()
        self.ParsedEmail = ParsedEmail
        self.Intake = Intake
        self.IntakeIssue = IntakeIssue
        self.IntakeIssueStatus = IntakeIssueStatus
        self.Issue = Issue
        self.Project = Project
        self.ProjectEmailAlias = ProjectEmailAlias
        self.ReceivedEmail = ReceivedEmail
        self.State = State
        self.StateGroup = StateGroup
        self.Workspace = Workspace

    def ingest(
        self,
        raw_email: bytes,
        message_id: Optional[str] = None,
    ) -> EmailIngestionResult:
        try:
            parsed = self.parser.parse(raw_email)
        except Exception as e:
            logger.error(f"Failed to parse email: {e}")
            return EmailIngestionResult(
                success=False,
                message=f"Failed to parse email: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        alias = self._find_alias(parsed.to_email)
        if not alias:
            logger.warning(f"No alias found for email: {parsed.to_email}")
            return EmailIngestionResult(
                success=False,
                message=f"No project configured for email address: {parsed.to_email}",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        project = alias.project
        workspace = project.workspace

        duplicate = self._check_duplicate(
            parsed=parsed,
            project=project,
            message_id=message_id,
        )
        if duplicate:
            logger.info(f"Duplicate email detected: {parsed.subject} from {parsed.from_email}")
            return EmailIngestionResult(
                success=True,
                is_duplicate=True,
                work_item_id=str(duplicate.intake_issue.issue_id) if duplicate.intake_issue else None,
                message="Email is a duplicate",
                status_code=status.HTTP_200_OK,
            )

        actor = workspace.owner

        intake = self.Intake.objects.filter(project=project, is_active=True).first()
        if not intake:
            intake = self.Intake.objects.create(
                name="Default Intake",
                project=project,
                workspace=workspace,
                created_by=actor,
                updated_by=actor,
            )

        triage_state = self.State.triage_objects.filter(
            project=project,
        ).first()

        if not triage_state:
            triage_state = self.State.objects.create(
                name="Triage",
                group=self.StateGroup.TRIAGE.value,
                project=project,
                workspace=workspace,
                color="#4E5355",
                sequence=65000,
                default=False,
            )

        subject = parsed.subject or "(No Subject)"
        body_html = self._get_description_html(parsed)

        with transaction.atomic():
            issue = self.Issue.objects.create(
                name=subject[:255],
                description_html=body_html,
                description_html_hash=None,
                state=triage_state,
                project=project,
                workspace=workspace,
                created_by=actor,
                updated_by=actor,
            )

            attachments = self._create_attachments(issue, parsed, project, workspace, actor)

            intake_issue = self.IntakeIssue.objects.create(
                intake=intake,
                issue=issue,
                source="EMAIL",
                source_email=parsed.from_email,
                status=self.IntakeIssueStatus.PENDING,
                created_by=actor,
                updated_by=actor,
            )

            self.ReceivedEmail.objects.create(
                message_id=message_id or f"unknown-{timezone.now().timestamp()}",
                subject_hash=self._hash_subject(parsed.subject),
                sender_email=parsed.from_email,
                project=project,
                workspace=workspace,
                intake_issue=intake_issue,
            )

        logger.info(f"Created work item {issue.id} from email: {subject}")

        return EmailIngestionResult(
            success=True,
            work_item_id=str(issue.id),
            message="Work item created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    def _find_alias(self, to_email: str) -> Optional["ProjectEmailAlias"]:
        if "@" not in to_email:
            return None

        alias_part, domain = to_email.rsplit("@", 1)
        return (
            self.ProjectEmailAlias.objects.filter(
                alias__iexact=alias_part,
                domain__iexact=domain,
                is_active=True,
            )
            .select_related("project__workspace")
            .first()
        )

    def _check_duplicate(
        self,
        parsed: "ParsedEmail",
        project: "Project",
        message_id: Optional[str] = None,
    ) -> Optional["ReceivedEmail"]:
        if message_id:
            existing = self.ReceivedEmail.objects.filter(
                message_id=message_id,
                project=project,
            ).first()
            if existing:
                return existing

        subject_hash = self._hash_subject(parsed.subject)
        cutoff_time = timezone.now() - timezone.timedelta(hours=DEDUP_WINDOW_HOURS)

        return self.ReceivedEmail.objects.filter(
            subject_hash=subject_hash,
            sender_email__iexact=parsed.from_email,
            project=project,
            received_at__gte=cutoff_time,
        ).first()

    def _hash_subject(self, subject: str) -> str:
        normalized = subject.strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _get_description_html(self, parsed: "ParsedEmail") -> str:
        if parsed.body_html:
            return self.parser.sanitize_html(parsed.body_html)
        if parsed.body_text:
            return self.parser._plain_text_to_html(parsed.body_text)
        return ""

    def _create_attachments(
        self,
        issue: "Issue",
        parsed: "ParsedEmail",
        project: "Project",
        workspace: "Workspace",
        actor,
    ) -> list:
        from io import BytesIO

        from plane.db.models import FileAsset

        created_assets = []

        for attachment in parsed.attachments:
            try:
                asset = FileAsset.objects.create(
                    workspace=workspace,
                    project=project,
                    issue=issue,
                    entity_type=FileAsset.EntityTypeContext.ISSUE_ATTACHMENT,
                    attributes={
                        "name": attachment.filename,
                        "size": len(attachment.content),
                    },
                    created_by=actor,
                )

                asset.asset.save(attachment.filename, BytesIO(attachment.content))
                asset.is_uploaded = True
                asset.save()
                created_assets.append(asset)
            except Exception as e:
                logger.warning(f"Failed to create attachment {attachment.filename}: {e}")

        for image in parsed.inline_images:
            try:
                asset = FileAsset.objects.create(
                    workspace=workspace,
                    project=project,
                    issue=issue,
                    entity_type=FileAsset.EntityTypeContext.ISSUE_ATTACHMENT,
                    attributes={
                        "name": image.filename or f"inline-{image.content_id}.png",
                        "size": len(image.content),
                    },
                    external_id=image.content_id,
                    external_source="email-inline",
                    created_by=actor,
                )

                asset.asset.save(image.filename or "inline-image.png", BytesIO(image.content))
                asset.is_uploaded = True
                asset.save()
                created_assets.append(asset)
            except Exception as e:
                logger.warning(f"Failed to create inline image {image.filename}: {e}")

        return created_assets
