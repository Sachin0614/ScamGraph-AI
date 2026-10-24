"""Tests for transactional database evidence storage."""

import sys
from dataclasses import asdict
from pathlib import Path

import pytest

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from scamgraph.database.database import Database
from scamgraph.utils.evidence_import import EvidenceImportRecord


def test_import_evidence_persists_records_and_creates_investigation(
    tmp_path: Path,
) -> None:
    database = Database(str(tmp_path / "evidence.sqlite"))
    records = [
        asdict(EvidenceImportRecord(type="Email", content="Message body", source="Inbox")),
        asdict(EvidenceImportRecord(type="URL", content="https://example.invalid")),
    ]

    investigation_id, imported_count = database.import_evidence(
        records,
        new_investigation_title="CSV investigation",
    )

    assert imported_count == 2
    assert database.list_investigations()[0]["title"] == "CSV investigation"
    saved = database.fetch_all(
        "SELECT type, source, content FROM evidence WHERE investigation_id = ? "
        "ORDER BY id",
        (investigation_id,),
    )
    assert [tuple(row) for row in saved] == [
        ("Email", "Inbox", "Message body"),
        ("URL", None, "https://example.invalid"),
    ]


def test_import_evidence_rolls_back_new_investigation_on_failure(
    tmp_path: Path,
) -> None:
    database = Database(str(tmp_path / "rollback.sqlite"))

    with pytest.raises(KeyError):
        database.import_evidence(
            [{"type": "Email"}],
            new_investigation_title="Must be rolled back",
        )

    assert database.list_investigations() == []


def test_import_evidence_can_append_to_existing_investigation(
    tmp_path: Path,
) -> None:
    database = Database(str(tmp_path / "existing.sqlite"))
    investigation_id, _ = database.import_evidence(
        [asdict(EvidenceImportRecord(type="Email", content="First item"))],
        new_investigation_title="Existing case",
    )

    _, imported_count = database.import_evidence(
        [asdict(EvidenceImportRecord(type="Domain", content="example.invalid"))],
        investigation_id=investigation_id,
    )

    assert imported_count == 1
    assert database.fetch_one(
        "SELECT COUNT(*) AS count FROM evidence WHERE investigation_id = ?",
        (investigation_id,),
    )["count"] == 2
