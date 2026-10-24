"""Tests for CSV evidence parsing."""

import sys
from pathlib import Path

import pytest

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from scamgraph.utils.evidence_import import (
    EvidenceImportRecord,
    parse_evidence_csv,
)


def test_parse_evidence_csv_normalizes_headers_and_types() -> None:
    records = parse_evidence_csv(
        b"\xef\xbb\xbftype, source , content \r\n"
        b" email ,Manual,\"Suspicious, urgent message\"\r\n"
    )

    assert records == [
        EvidenceImportRecord(
            type="Email",
            content="Suspicious, urgent message",
            source="Manual",
        )
    ]


def test_parse_evidence_csv_allows_missing_optional_source() -> None:
    assert parse_evidence_csv("type,content\nURL,https://example.invalid\n") == [
        EvidenceImportRecord(type="URL", content="https://example.invalid")
    ]


def test_parse_evidence_csv_reports_invalid_rows_without_partial_results() -> None:
    with pytest.raises(ValueError, match="Row 2.*type must be one of"):
        parse_evidence_csv("type,content\nUnknown,value\nEmail,\n")


def test_parse_evidence_csv_rejects_invalid_encoding_and_headers() -> None:
    with pytest.raises(ValueError, match="UTF-8"):
        parse_evidence_csv(b"\xff")
    with pytest.raises(ValueError, match="Missing required CSV column"):
        parse_evidence_csv("type,source\nEmail,mail\n")
    with pytest.raises(ValueError, match="malformed"):
        parse_evidence_csv('type,content\nEmail,"unclosed content')
