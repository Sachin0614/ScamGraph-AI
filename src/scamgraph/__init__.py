"""
ScamGraph AI - Main Package
AI-powered scam investigation platform.
"""

__version__ = "1.0.0"
__author__ = "ScamGraph AI Team"
__description__ = "Modern dark-themed AI scam investigation application"

from scamgraph.config import config, get_logger, setup_logging
from scamgraph.database import db, get_db
from scamgraph.utils import (
    calculate_risk_score,
    extract_domains,
    extract_emails,
    extract_phones,
    extract_urls,
    format_timestamp,
    generate_id,
    parse_domain,
    safe_dict_get,
    sanitize_text,
    truncate,
)

__all__ = [
    "calculate_risk_score",
    "config",
    "db",
    "extract_domains",
    "extract_emails",
    "extract_phones",
    "extract_urls",
    "format_timestamp",
    "generate_id",
    "get_db",
    "get_logger",
    "parse_domain",
    "safe_dict_get",
    "sanitize_text",
    "setup_logging",
    "truncate",
]