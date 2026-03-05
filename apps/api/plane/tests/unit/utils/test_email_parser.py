# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from io import BytesIO

import pytest

from plane.utils.email_parser import EmailParser, ParsedAttachment


class TestEmailParser:
    """Tests for the EmailParser service."""

    def test_parse_simple_text_email(self):
        """Test parsing a simple plain text email."""
        raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: Test Email
Content-Type: text/plain

This is a simple test email body.
"""
        parser = EmailParser()
        result = parser.parse(raw_email)

        assert result.subject == "Test Email"
        assert result.body_text == "This is a simple test email body."
        assert result.from_email == "sender@example.com"
        assert result.to_email == "recipient@example.com"

    def test_parse_simple_html_email(self):
        """Test parsing a simple HTML email."""
        raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: HTML Email
Content-Type: text/html

<html><body><p>This is an <strong>HTML</strong> email.</p></body></html>
"""
        parser = EmailParser()
        result = parser.parse(raw_email)

        assert result.subject == "HTML Email"
        assert result.body_html is not None
        assert "HTML" in result.body_html

    def test_parse_multipart_alternative(self):
        """Test parsing a multipart/alternative email (text + HTML)."""
        raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: Multipart Email
Content-Type: multipart/alternative; boundary="boundary"

--boundary
Content-Type: text/plain

This is the plain text version.

--boundary
Content-Type: text/html

<html><body><p>This is the <strong>HTML</strong> version.</p></body></html>

--boundary--
"""
        parser = EmailParser()
        result = parser.parse(raw_email)

        assert result.subject == "Multipart Email"
        assert result.body_text is not None
        assert "plain text version" in result.body_text
        assert result.body_html is not None
        assert "HTML" in result.body_html

    def test_parse_multipart_mixed_with_attachment(self):
        """Test parsing a multipart/mixed email with attachment."""
        import base64

        attachment_content = b"This is a test attachment file."
        attachment_b64 = base64.b64encode(attachment_content).decode()

        raw_email = f"""From: sender@example.com
To: recipient@example.com
Subject: Email with Attachment
Content-Type: multipart/mixed; boundary="boundary"

--boundary
Content-Type: text/plain

This is the email body with an attachment.

--boundary
Content-Type: application/octet-stream; name="test.txt"
Content-Disposition: attachment; filename="test.txt"
Content-Transfer-Encoding: base64

{attachment_b64}

--boundary--
"""
        parser = EmailParser()
        result = parser.parse(raw_email.encode())

        assert result.subject == "Email with Attachment"
        assert "email body" in result.body_text
        assert len(result.attachments) == 1
        assert result.attachments[0].filename == "test.txt"
        assert result.attachments[0].content == attachment_content

    def test_parse_inline_image(self):
        """Test parsing an email with inline image."""
        import base64

        image_content = b"\x89PNG\r\n\x1a\n"  # PNG magic bytes
        image_b64 = base64.b64encode(image_content).decode()

        raw_email = f"""From: sender@example.com
To: recipient@example.com
Subject: Email with Inline Image
Content-Type: multipart/related; boundary="boundary"

--boundary
Content-Type: text/plain

Check out this image:

--boundary
Content-Type: image/png
Content-ID: <image123>
Content-Disposition: inline

{image_b64}

--boundary--
"""
        parser = EmailParser()
        result = parser.parse(raw_email.encode())

        assert result.subject == "Email with Inline Image"
        assert len(result.inline_images) >= 0
        if result.inline_images:
            assert result.inline_images[0].content_id == "image123"

    def test_get_plain_text_body_prefers_text(self):
        """Test that get_plain_text_body prefers text/plain over text/html."""
        raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: Test
Content-Type: multipart/alternative; boundary="boundary"

--boundary
Content-Type: text/plain

Plain text body.

--boundary
Content-Type: text/html

<html><body><p>HTML body.</p></body></html>

--boundary--
"""
        parser = EmailParser()
        result = parser.parse(raw_email)

        plain_text = parser.get_plain_text_body(result)
        assert plain_text == "Plain text body."

    def test_get_html_body_sanitizes_html(self):
        """Test that get_html_body sanitizes HTML content."""
        raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: Test
Content-Type: text/html

<html><body><script>alert('xss')</script><p>Hello</p></body></html>
"""
        parser = EmailParser()
        result = parser.parse(raw_email)

        html = parser.get_html_body(result)
        assert html is not None
        assert "<script>" not in html
        assert "<p>Hello</p>" in html

    def test_decode_encoded_subject(self):
        """Test decoding encoded subject lines."""
        import email.header

        encoded_subject = email.header.make_header([(b"Test Subject =?utf-8?q?=E2=9C=93?=", "utf-8")])
        raw_email = f"""From: sender@example.com
To: recipient@example.com
Subject: {str(encoded_subject)}
Content-Type: text/plain

Test body.
"""
        parser = EmailParser()
        result = parser.parse(raw_email.encode())

        assert "Test Subject" in result.subject

    def test_truncate_large_body(self):
        """Test that large bodies are truncated."""
        large_text = "A" * (11 * 1024 * 1024)  # 11MB

        raw_email = f"""From: sender@example.com
To: recipient@example.com
Subject: Large Email
Content-Type: text/plain

{large_text}
"""
        parser = EmailParser()
        result = parser.parse(raw_email.encode())

        assert len(result.body_text) <= EmailParser.MAX_BODY_SIZE


class TestEmailWorkItemCreator:
    """Tests for the EmailWorkItemCreator service."""

    def test_parsed_attachment_dataclass(self):
        """Test ParsedAttachment dataclass."""
        attachment = ParsedAttachment(
            filename="test.txt",
            content_type="text/plain",
            content=b"test content",
            is_inline=False,
            content_id=None,
        )

        assert attachment.filename == "test.txt"
        assert attachment.content_type == "text/plain"
        assert attachment.content == b"test content"
        assert attachment.is_inline is False
        assert attachment.content_id is None
