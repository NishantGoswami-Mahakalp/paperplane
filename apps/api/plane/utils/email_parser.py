# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import base64
import email
import logging
from dataclasses import dataclass
from email.message import Message
from email.policy import default
from io import BytesIO
from typing import Optional

# Django imports
from django.utils.html import strip_tags

# Third party imports
import nh3
from bs4 import BeautifulSoup

# Module imports
from plane.utils.content_validator import validate_html_content

logger = logging.getLogger("plane.api")


@dataclass
class ParsedAttachment:
    filename: str
    content_type: str
    content: bytes
    is_inline: bool = False
    content_id: Optional[str] = None


@dataclass
class ParsedEmail:
    subject: str
    body_text: Optional[str]
    body_html: Optional[str]
    from_email: str
    to_email: str
    attachments: list[ParsedAttachment]
    inline_images: list[ParsedAttachment]


class EmailParser:
    """
    Service class for parsing MIME email messages.
    Handles multipart/mixed, multipart/alternative, and simple messages.
    """

    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB

    CUSTOM_TAGS = {
        "mention-component",
        "label",
        "input",
        "image-component",
    }
    ALLOWED_TAGS = nh3.ALLOWED_TAGS | CUSTOM_TAGS

    ATTRIBUTES = {
        "*": {
            "class",
            "id",
            "title",
            "role",
            "aria-label",
            "aria-hidden",
            "style",
            "start",
            "type",
            "xmlns",
            "data-tight",
            "data-node-type",
            "data-type",
            "data-checked",
            "data-background-color",
            "data-text-color",
            "data-name",
            "data-id",
            "data-icon-name",
            "data-icon-color",
            "data-background",
            "data-emoji-unicode",
            "data-emoji-url",
            "data-logo-in-use",
            "data-block-type",
        },
        "a": {"href", "target"},
        "image-component": {
            "id",
            "width",
            "height",
            "aspectRatio",
            "aspectratio",
            "src",
            "alignment",
            "status",
        },
        "img": {
            "width",
            "height",
            "aspectRatio",
            "aspectratio",
            "alignment",
            "src",
            "alt",
            "title",
        },
        "mention-component": {"id", "entity_identifier", "entity_name"},
        "th": {
            "colspan",
            "rowspan",
            "colwidth",
            "background",
            "style",
        },
        "td": {
            "colspan",
            "rowspan",
            "colwidth",
            "background",
            "textColor",
            "textcolor",
            "style",
        },
        "tr": {"background", "textColor", "textcolor", "style"},
        "pre": {"language"},
        "code": {"language", "spellcheck"},
        "input": {"type", "checked"},
    }

    SAFE_PROTOCOLS = {"http", "https", "mailto", "tel"}

    def parse(self, raw_email: bytes) -> ParsedEmail:
        """
        Parse a raw email message into its components.

        Args:
            raw_email: The raw email bytes

        Returns:
            ParsedEmail object containing parsed content
        """
        msg = email.message_from_bytes(raw_email, policy=default)

        subject = self._get_subject(msg)
        from_email = self._get_from_email(msg)
        to_email = self._get_to_email(msg)

        body_text = None
        body_html = None
        attachments = []
        inline_images = []

        if msg.is_multipart():
            body_text, body_html, attachments, inline_images = self._parse_multipart(msg)
        else:
            body_text, body_html = self._parse_singlepart(msg)

        body_text = self._truncate_body(body_text)
        body_html = self._truncate_body(body_html)

        return ParsedEmail(
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            from_email=from_email,
            to_email=to_email,
            attachments=attachments,
            inline_images=inline_images,
        )

    def _get_subject(self, msg: Message) -> str:
        subject = msg.get("Subject", "")
        if subject:
            decoded = email.header.decode_header(subject)
            subject = " ".join(
                part.decode(encoding or "utf-8") if isinstance(part, bytes) else part for part, encoding in decoded
            )
        return subject.strip() or "(No Subject)"

    def _get_from_email(self, msg: Message) -> str:
        from_header = msg.get("From", "")
        return self._extract_email(from_header)

    def _get_to_email(self, msg: Message) -> str:
        to_header = msg.get("To", "")
        return self._extract_email(to_header)

    def _extract_email(self, header_value: str) -> str:
        import re

        match = re.search(r"<(.+?)>", header_value)
        if match:
            return match.group(1).strip()
        return header_value.strip()

    def _parse_multipart(
        self, msg: Message
    ) -> tuple[Optional[str], Optional[str], list[ParsedAttachment], list[ParsedAttachment]]:
        body_text = None
        body_html = None
        attachments = []
        inline_images = []

        for part in msg.walk():
            content_disposition = part.get("Content-Disposition", "")
            is_inline = "inline" in content_disposition.lower()
            is_attachment = "attachment" in content_disposition.lower()

            if is_attachment or is_inline:
                parsed = self._extract_attachment(part, is_inline)
                if parsed:
                    if is_inline and parsed.content_type.startswith("image/"):
                        inline_images.append(parsed)
                    else:
                        attachments.append(parsed)
                continue

            content_type = part.get_content_type()

            if content_type == "text/plain" and body_text is None:
                body_text = self._extract_text_content(part)
            elif content_type == "text/html" and body_html is None:
                body_html = self._extract_html_content(part)

        return body_text, body_html, attachments, inline_images

    def _parse_singlepart(self, msg: Message) -> tuple[Optional[str], Optional[str]]:
        content_type = msg.get_content_type()
        body_text = None
        body_html = None

        if content_type == "text/plain":
            body_text = self._extract_text_content(msg)
        elif content_type == "text/html":
            body_html = self._extract_html_content(msg)
        else:
            body_text = self._extract_text_content(msg)

        return body_text, body_html

    def _extract_text_content(self, part: Message) -> Optional[str]:
        try:
            content = part.get_content()
            if isinstance(content, bytes):
                charset = part.get_content_charset() or "utf-8"
                return content.decode(charset, errors="replace")
            return str(content)
        except Exception as e:
            logger.warning(f"Failed to extract text content: {e}")
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
            except Exception:
                pass
        return None

    def _extract_html_content(self, part: Message) -> Optional[str]:
        try:
            content = part.get_content()
            if isinstance(content, bytes):
                charset = part.get_content_charset() or "utf-8"
                return content.decode(charset, errors="replace")
            return str(content)
        except Exception as e:
            logger.warning(f"Failed to extract HTML content: {e}")
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
            except Exception:
                pass
        return None

    def _extract_attachment(self, part: Message, is_inline: bool) -> Optional[ParsedAttachment]:
        try:
            filename = part.get_filename()
            if not filename:
                return None

            decoded = part.get_payload(decode=True)
            if not decoded:
                return None

            import email.header

            if isinstance(filename, str):
                decoded_header = email.header.decode_header(filename)
                filename = " ".join(
                    part.decode(encoding or "utf-8") if isinstance(part, bytes) else part
                    for part, encoding in decoded_header
                )

            content_type = part.get_content_type()

            content_id = None
            if is_inline:
                content_id = part.get("Content-ID", "").strip("<>")
            elif content_type.startswith("image/"):
                content_id = part.get("Content-ID", "").strip("<>")

            return ParsedAttachment(
                filename=filename,
                content_type=content_type,
                content=decoded,
                is_inline=is_inline or bool(content_id),
                content_id=content_id,
            )
        except Exception as e:
            logger.warning(f"Failed to extract attachment: {e}")
            return None

    def _truncate_body(self, body: Optional[str]) -> Optional[str]:
        if body and len(body) > self.MAX_BODY_SIZE:
            return body[: self.MAX_BODY_SIZE]
        return body

    def get_plain_text_body(self, parsed: ParsedEmail) -> Optional[str]:
        """
        Get the plain text body, with preference for text/plain over text/html.
        """
        if parsed.body_text:
            return parsed.body_text
        if parsed.body_html:
            return self._html_to_plain_text(parsed.body_html)
        return None

    def get_html_body(self, parsed: ParsedEmail) -> Optional[str]:
        """
        Get the sanitized HTML body.
        """
        if not parsed.body_html:
            if parsed.body_text:
                return self._plain_text_to_html(parsed.body_text)
            return None

        return self.sanitize_html(parsed.body_html)

    def sanitize_html(self, html_content: str) -> str:
        """
        Sanitize HTML content using nh3 for security.
        """
        if not html_content:
            return ""

        is_valid, error_msg, clean_html = validate_html_content(html_content)
        if is_valid and clean_html:
            return clean_html

        return html_content

    def _html_to_plain_text(self, html: str) -> str:
        """Convert HTML to plain text by stripping tags."""
        return strip_tags(html).strip()

    def _plain_text_to_html(self, text: str) -> str:
        """Convert plain text to simple HTML."""
        if not text:
            return ""
        lines = text.split("\n")
        html_lines = []
        for line in lines:
            if line.strip():
                html_lines.append(f"<p>{line}</p>")
            else:
                html_lines.append("<br>")
        return "".join(html_lines)


class EmailWorkItemCreator:
    """
    Service class for creating work items from parsed emails.
    """

    def __init__(self, workspace, project, actor):
        self.workspace = workspace
        self.project = project
        self.actor = actor

    def create_work_item(
        self,
        parsed_email: ParsedEmail,
        intake=None,
        state=None,
    ):
        """
        Create a work item (Issue) from a parsed email.

        Args:
            parsed_email: The parsed email content
            intake: Optional intake to link the work item to
            state: Optional state for the work item

        Returns:
            Tuple of (Issue, list of FileAsset attachments)
        """
        from plane.db.models import Issue, FileAsset

        subject = parsed_email.subject or "(No Subject)"
        body_html = parsed_email.body_html
        body_text = parsed_email.body_text

        if body_html:
            description_html = body_html
        elif body_text:
            parser = EmailParser()
            description_html = parser._plain_text_to_html(body_text)
        else:
            description_html = ""

        if description_html:
            parser = EmailParser()
            description_html = parser.sanitize_html(description_html)

        issue = Issue.objects.create(
            name=subject[:255],
            description_html=description_html,
            description_html_hash=None,
            state=state,
            project=self.project,
            workspace=self.workspace,
            created_by=self.actor,
            updated_by=self.actor,
        )

        attachments = []
        if parsed_email.attachments:
            attachments = self._create_attachments(issue, parsed_email.attachments)

        if parsed_email.inline_images:
            inline_attachments = self._create_inline_images(issue, parsed_email.inline_images)
            attachments.extend(inline_attachments)

        if intake:
            from plane.db.models import IntakeIssue, IntakeIssueStatus

            IntakeIssue.objects.create(
                intake=intake,
                issue=issue,
                source="EMAIL",
                source_email=parsed_email.from_email,
                status=IntakeIssueStatus.PENDING,
                created_by=self.actor,
                updated_by=self.actor,
            )

        return issue, attachments

    def _create_attachments(self, issue, attachments: list[ParsedAttachment]) -> list:
        from plane.db.models import FileAsset

        created_assets = []
        for attachment in attachments:
            try:
                asset = FileAsset.objects.create(
                    workspace=self.workspace,
                    project=self.project,
                    issue=issue,
                    entity_type=FileAsset.EntityTypeContext.ISSUE_ATTACHMENT,
                    attributes={
                        "name": attachment.filename,
                        "size": len(attachment.content),
                    },
                    created_by=self.actor,
                )

                asset.asset.save(attachment.filename, BytesIO(attachment.content))
                asset.is_uploaded = True
                asset.save()
                created_assets.append(asset)
            except Exception as e:
                logger.warning(f"Failed to create attachment {attachment.filename}: {e}")

        return created_assets

    def _create_inline_images(self, issue, inline_images: list[ParsedAttachment]) -> list:
        from plane.db.models import FileAsset

        created_assets = []
        for image in inline_images:
            try:
                asset = FileAsset.objects.create(
                    workspace=self.workspace,
                    project=self.project,
                    issue=issue,
                    entity_type=FileAsset.EntityTypeContext.ISSUE_ATTACHMENT,
                    attributes={
                        "name": image.filename or f"inline-{image.content_id}.png",
                        "size": len(image.content),
                    },
                    external_id=image.content_id,
                    external_source="email-inline",
                    created_by=self.actor,
                )

                asset.asset.save(image.filename or "inline-image.png", BytesIO(image.content))
                asset.is_uploaded = True
                asset.save()
                created_assets.append(asset)
            except Exception as e:
                logger.warning(f"Failed to create inline image {image.filename}: {e}")

        return created_assets
