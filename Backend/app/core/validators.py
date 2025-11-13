"""
Input validation utilities and custom validators.
Provides security-focused validation for user inputs.
"""
import re
import html
from typing import Any, Optional
from pydantic import field_validator
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Utility class for input validation and sanitization."""

    # Regex patterns
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^\+?[1-9]\d{1,14}$'  # E.164 format
    UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

    # XSS dangerous patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',  # onclick, onload, etc.
        r'<iframe',
        r'<embed',
        r'<object',
    ]

    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Remove or escape HTML/JavaScript to prevent XSS attacks.

        Args:
            text: Input text that may contain malicious code

        Returns:
            Sanitized text with HTML entities escaped
        """
        if not text:
            return text

        # Escape HTML entities
        sanitized = html.escape(text)

        # Check for dangerous patterns
        for pattern in InputValidator.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential XSS attempt detected: {pattern}")

        return sanitized

    @staticmethod
    def validate_email(email: Optional[str]) -> Optional[str]:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            Validated email in lowercase

        Raises:
            ValueError: If email format is invalid
        """
        if not email:
            return None

        email = email.strip().lower()

        if not re.match(InputValidator.EMAIL_PATTERN, email):
            raise ValueError("Invalid email format")

        if len(email) > 254:  # RFC 5321
            raise ValueError("Email address too long")

        return email

    @staticmethod
    def validate_phone(phone: Optional[str]) -> Optional[str]:
        """
        Validate and normalize phone number.

        Args:
            phone: Phone number to validate

        Returns:
            Normalized phone number

        Raises:
            ValueError: If phone format is invalid
        """
        if not phone:
            return None

        # Remove common formatting characters
        phone = re.sub(r'[\s\-\(\)\.]+', '', phone)

        # Check against E.164 format (international standard)
        if not re.match(InputValidator.PHONE_PATTERN, phone):
            raise ValueError("Invalid phone format. Use international format: +34666777888")

        if len(phone) > 15:
            raise ValueError("Phone number too long")

        return phone

    @staticmethod
    def validate_session_id(session_id: Optional[str]) -> Optional[str]:
        """
        Validate session ID format.

        Args:
            session_id: Session ID to validate

        Returns:
            Validated session ID

        Raises:
            ValueError: If session ID format is invalid
        """
        if not session_id:
            return None

        session_id = session_id.strip()

        # Allow UUID format or session-{timestamp} format
        if re.match(InputValidator.UUID_PATTERN, session_id, re.IGNORECASE):
            return session_id.lower()

        if re.match(r'^session-\d{13,}$', session_id):
            return session_id

        raise ValueError("Invalid session ID format")

    @staticmethod
    def sanitize_text_field(text: str, max_length: int = 500) -> str:
        """
        Sanitize general text fields.

        Args:
            text: Text to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized text

        Raises:
            ValueError: If text is too long
        """
        if not text:
            return ""

        text = text.strip()

        if len(text) > max_length:
            raise ValueError(f"Text exceeds maximum length of {max_length} characters")

        # Remove null bytes
        text = text.replace('\x00', '')

        # Escape HTML for XSS prevention
        text = InputValidator.sanitize_html(text)

        return text


# Pydantic field validators (for use in models)

def email_validator(cls, v: Optional[str]) -> Optional[str]:
    """Pydantic field validator for email."""
    return InputValidator.validate_email(v)


def phone_validator(cls, v: Optional[str]) -> Optional[str]:
    """Pydantic field validator for phone."""
    return InputValidator.validate_phone(v)


def session_id_validator(cls, v: Optional[str]) -> Optional[str]:
    """Pydantic field validator for session ID."""
    return InputValidator.validate_session_id(v)
