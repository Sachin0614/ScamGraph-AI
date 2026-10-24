"""CSV parsing helpers for offline evidence imports."""

import csv
import io
from dataclasses import dataclass

EVIDENCE_TYPES = (
    "Email",
    "Phone Number",
    "Domain",
    "URL",
    "Text Message",
    "Screenshot",
    "Document",
    "Other",
)

_EVIDENCE_TYPES_BY_KEY = {value.casefold(): value for value in EVIDENCE_TYPES}


@dataclass(frozen=True)
class EvidenceImportRecord:
    """A validated evidence row ready to be stored."""

    type: str
    content: str
    source: str | None = None


def parse_evidence_csv(csv_content: bytes | str) -> list[EvidenceImportRecord]:
    """Parse CSV evidence rows with required ``type`` and ``content`` columns."""
    if isinstance(csv_content, bytes):
        try:
            csv_text = csv_content.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError("The CSV file must use UTF-8 encoding.") from error
    else:
        csv_text = csv_content.lstrip("\ufeff")

    reader = csv.DictReader(io.StringIO(csv_text, newline=""), strict=True)
    if reader.fieldnames is None:
        raise ValueError("The CSV file is empty or has no header row.")

    headers = [header.strip().casefold() if header else "" for header in reader.fieldnames]
    if len(headers) != len(set(headers)):
        raise ValueError("The CSV file contains duplicate column names.")
    missing_headers = {"type", "content"} - set(headers)
    if missing_headers:
        missing = ", ".join(sorted(missing_headers))
        raise ValueError(f"Missing required CSV column(s): {missing}.")

    records: list[EvidenceImportRecord] = []
    errors: list[str] = []
    header_indexes = {header: index for index, header in enumerate(headers)}

    try:
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                errors.append(f"Row {row_number}: too many columns.")
                continue

            raw_type = row.get(reader.fieldnames[header_indexes["type"]], "")
            raw_content = row.get(reader.fieldnames[header_indexes["content"]], "")
            raw_source = (
                row.get(reader.fieldnames[header_indexes["source"]], "")
                if "source" in header_indexes
                else ""
            )
            evidence_type = _EVIDENCE_TYPES_BY_KEY.get((raw_type or "").strip().casefold())
            content = (raw_content or "").strip()

            if not evidence_type:
                errors.append(
                    f"Row {row_number}: type must be one of "
                    f"{', '.join(EVIDENCE_TYPES)}."
                )
                continue
            if not content:
                errors.append(f"Row {row_number}: content is required.")
                continue

            records.append(
                EvidenceImportRecord(
                    type=evidence_type,
                    content=content,
                    source=(raw_source or "").strip() or None,
                )
            )
    except csv.Error as error:
        raise ValueError(f"The CSV file is malformed: {error}") from error

    if errors:
        raise ValueError("CSV validation failed:\n" + "\n".join(errors))
    if not records:
        raise ValueError("The CSV file contains no evidence rows.")
    return records
