# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import logging
import re

# Third party imports
from rest_framework.throttling import SimpleRateThrottle
from plane.utils.ip_address import get_client_ip

logger = logging.getLogger("plane")


class IntakeSubmissionRateThrottle(SimpleRateThrottle):
    """
    Rate limiter for intake form submissions based on IP address.
    Tracks submissions per IP to prevent abuse.
    """

    scope = "intake_submission"
    rate = "10/minute"  # Default: 10 submissions per minute per IP

    def get_cache_key(self, request, view):
        ip = get_client_ip(request)
        if ip is None:
            return None

        # Use the intake form ID to allow different limits per form
        form_id = view.kwargs.get("form_id", "global")
        return f"{self.scope}:{form_id}:{ip}"

    def throttle_failure(self):
        """
        Log when a submission is blocked due to rate limiting.
        """
        return False

    def allow_request(self, request, view):
        # Get the form_id from view kwargs
        form_id = view.kwargs.get("form_id", "global")

        allowed = super().allow_request(request, view)

        if not allowed:
            ip = get_client_ip(request)
            logger.warning(
                "Intake submission rate limit exceeded",
                extra={
                    "ip_address": ip,
                    "form_id": str(form_id),
                    "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                },
            )

        return allowed


class IntakeSubmissionPerFormRateThrottle(SimpleRateThrottle):
    """
    Rate limiter that tracks submissions per form per IP.
    Allows configuring different limits per form.
    """

    scope = "intake_form_submission"

    def get_rate(self):
        """
        Get the rate from settings or use default.
        """
        from django.conf import settings

        return getattr(settings, "INTAKE_SUBMISSION_RATE", "10/minute")

    def get_cache_key(self, request, view):
        ip = get_client_ip(request)
        if ip is None:
            return None

        form_id = view.kwargs.get("form_id", "global")
        return f"{self.scope}:{form_id}:{ip}"


def sanitize_input(value, field_type="text"):
    """
    Sanitize user input to prevent injection attacks.

    Args:
        value: The input value to sanitize
        field_type: The type of field (text, email, url, etc.)

    Returns:
        Sanitized value
    """
    if value is None:
        return None

    if isinstance(value, str):
        # Remove null bytes
        value = value.replace("\x00", "")

        # For text fields, strip leading/trailing whitespace
        if field_type in ["text", "textarea"]:
            value = value.strip()

        # Basic XSS prevention - remove script tags
        value = re.sub(r"<\s*script[^>]*>.*?</script>", "", value, flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(r"<\s*script[^>]*/?>", "", value, flags=re.IGNORECASE)

        # Remove event handlers
        value = re.sub(r"\s*on\w+\s*=", " data-removed=", value, flags=re.IGNORECASE)

        # For URL fields, validate URL format
        if field_type == "url":
            # Only allow http and https
            if value and not value.startswith(("http://", "https://")):
                value = "https://" + value if not value.startswith("//") else value

        # For email fields, basic validation
        if field_type == "email":
            # Basic email regex
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, value):
                # Return None if email is invalid
                return None

    return value


def log_abuse_attempt(request, form_id, abuse_type, details=None):
    """
    Log abuse attempts for monitoring and analysis.

    Args:
        request: The HTTP request
        form_id: The ID of the intake form
        abuse_type: Type of abuse (rate_limit, invalid_captcha, suspicious_input, etc.)
        details: Additional details about the abuse
    """
    ip = get_client_ip(request)

    logger.warning(
        f"Intake form abuse attempt: {abuse_type}",
        extra={
            "abuse_type": abuse_type,
            "ip_address": ip,
            "form_id": str(form_id),
            "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
            "path": request.path,
            "method": request.method,
            "details": details or {},
        },
    )


def validate_captcha(request, captcha_token=None):
    """
    Validate captcha token. Currently implements a simple honeypot check.
    Can be extended to support reCAPTCHA, hCaptcha, etc.

    Args:
        request: The HTTP request
        captcha_token: Optional captcha token from the client

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Simple honeypot field check
    honeypot_field = request.data.get("website_url", "") or request.data.get("hp_field", "")

    # If honeypot field has any value, it's likely a bot
    if honeypot_field:
        return False, "Invalid submission detected"

    # If a captcha token is required but not provided
    if captcha_token is None:
        # For now, we make captcha optional - can be made mandatory via settings
        from django.conf import settings

        captcha_required = getattr(settings, "INTAKE_CAPTCHA_REQUIRED", False)

        if captcha_required:
            return False, "Captcha validation required"

    # Add actual captcha validation here when implementing (e.g., reCAPTCHA)
    # if captcha_token:
    #     # Validate with Google reCAPTCHA or similar
    #     pass

    return True, None
