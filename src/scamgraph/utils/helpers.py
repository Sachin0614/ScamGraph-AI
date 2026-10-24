"""
ScamGraph AI - Utility Functions
Common helper functions used across the application.
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with optional prefix.

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique ID string
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    hash_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    return f"{prefix}{timestamp}{hash_part}"


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """
    Sanitize text input for safe storage and display.

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""
    # Remove null bytes and control characters
    text = text.replace("\x00", "").replace("\r", " ")
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "... [truncated]"
    return text.strip()


def extract_emails(text: str) -> list[str]:
    """
    Extract email addresses from text.

    Args:
        text: Input text

    Returns:
        List of unique email addresses
    """
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    emails = re.findall(email_pattern, text)
    return list(set(emails))


def extract_phones(text: str) -> list[str]:
    """
    Extract phone numbers from text (US format).

    Args:
        text: Input text

    Returns:
        List of unique phone numbers
    """
    phone_pattern = r"(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})"
    matches = re.findall(phone_pattern, text)
    phones = [f"({m[0]}) {m[1]}-{m[2]}" for m in matches]
    return list(set(phones))


def extract_domains(text: str) -> list[str]:
    """
    Extract domain names from text.

    Args:
        text: Input text

    Returns:
        List of unique domains
    """
    domain_pattern = r"(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)"
    domains = re.findall(domain_pattern, text)
    # Filter out common false positives
    filtered = [d for d in domains if not d.endswith((".png", ".jpg", ".gif", ".css", ".js"))]
    return list(set(filtered))


def extract_urls(text: str) -> list[str]:
    """
    Extract URLs from text.

    Args:
        text: Input text

    Returns:
        List of unique URLs
    """
    url_pattern = r"https?://[^\s<>\"']+"
    urls = re.findall(url_pattern, text)
    return list(set(urls))


def parse_domain(url: str) -> str | None:
    """
    Extract domain from URL.

    Args:
        url: URL string

    Returns:
        Domain name or None
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower().replace("www.", "")
    except ValueError:
        return None


def calculate_risk_score(indicators: dict[str, float], weights: dict[str, float] | None = None) -> float:
    """
    Calculate weighted risk score from indicators.

    Args:
        indicators: Dict of indicator name -> score (0.0 to 1.0)
        weights: Optional dict of indicator name -> weight

    Returns:
        Risk score from 0.0 to 100.0
    """
    if not indicators:
        return 0.0

    if weights is None:
        weights = {k: 1.0 for k in indicators}

    total_weight = sum(weights.get(k, 1.0) for k in indicators)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(
        indicators[k] * weights.get(k, 1.0) for k in indicators
    )
    return round((weighted_sum / total_weight) * 100, 1)


def format_timestamp(dt: datetime | None = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime as string.

    Args:
        dt: Datetime object (defaults to now)
        fmt: Format string

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime(fmt)


def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.

    Args:
        text: Input text
        length: Maximum length
        suffix: Suffix to append if truncated

    Returns:
        Truncated text
    """
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def safe_dict_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get value from nested dict using dot notation.

    Args:
        data: Dictionary
        key: Key in dot notation (e.g., "user.email")
        default: Default value if not found

    Returns:
        Value or default
    """
    keys = key.split(".")
    current = data
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    return current