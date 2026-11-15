"""Validate Phase 2 source-audit register without promoting source checks to file audits.

Run: python scripts/validate_phase2_source_audit.py
"""
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PILOT = DOCS / "phase2_source_audit_2026-11-15.json"


def https_url(value):
    if not isinstance(value, str):
        return False
    url = urlparse(value)
    return url.scheme == "https" and bool(url.hostname)


def validate():
    raw = json.loads(PILOT.read_text(encoding="utf-8"))
    catalogue = json.loads((DOCS / "datasets.json").read_text(encoding="utf-8"))
    by_id = {d["id"]: d for d in catalogue}
    passports = json.loads((DOCS / "readiness_passports.json").read_text(encoding="utf-8"))["passports"]
    entries = raw["entries"]
    errors = []

    if raw.get("schema_version") != 1:
        errors.append("wrong schema_version")
    if raw.get("audit_id") != "ionsense-phase2-pilot-2026-11-15":
        errors.append("wrong pilot identifier")
    if len(entries) != 15:
        errors.append("pilot must contain exactly 15 distinct source records")
    ids = [e.get("dataset_id") for e in entries]
    if len(set(ids)) != len(ids):
        errors.append("duplicate dataset IDs")
    if raw.get("source_documentation_reviewed") != len(entries):
        errors.append("unreconciled source documentation count")
    actual_file_audits = sum(e.get("raw_file_audit", {}).get("status") == "file_verified" for e in entries)
    if raw.get("raw_files_independently_inspected") != actual_file_audits:
        errors.append("file audit summary does not match evidence")
    if raw.get("status") == "documentation_review_completed_raw_data_pending" and actual_file_audits:
        errors.append("summary status cannot claim raw data pending when file audits exist")

    for e in entries:
        id_ = e.get("dataset_id")
        label = str(id_) + ": "
        if id_ not in by_id or id_ not in passports:
            errors.append(label + "missing catalogue/passport ID")
            continue
        if e.get("dataset_name") != by_id[id_]["name"]:
            errors.append(label + "name disagrees with original catalogue")
        if e.get("source_url") != by_id[id_]["url"]:
            errors.append(label + "source URL disagrees with original catalogue")
        source = e.get("source_documentation")
        if not isinstance(source, dict) or not source.get("status", "").endswith(
            ("reviewed", "reviewed_portal_js_only", "reviewed_repository_blocked")
        ):
            # Some statuses include an extra suffix (e.g. agency_repository_page_reviewed).
            errors.append(label + "source review stage is invalid")
            continue
        if not https_url(source.get("evidence_url")):
            errors.append(label + "source evidence URL missing")
        facts = source.get("facts", [])
        if not isinstance(facts, list) or not facts or any(
            not isinstance(x, str) or len(x.strip()) < 30 for x in facts
        ):
            errors.append(label + "missing meaningful source findings")
        flags = e.get("review_flags", [])
        if not isinstance(flags, list) or not flags:
            errors.append(label + "missing review flags")

        file_audit = e.get("raw_file_audit", {})
        if file_audit.get("status") == "not_performed":
            if file_audit.get("files_inspected") != 0:
                errors.append(label + "file inspection incorrectly counted")
            if any(file_audit.get(x) for x in (
                "sha256_recomputed", "raw_columns_checked", "cell_ids_checked",
                "train_test_split_checked",
            )):
                errors.append(label + "file-level validation asserted without inspection")
            if not file_audit.get("blocker"):
                errors.append(label + "missing file audit blocker")
        elif file_audit.get("status") == "file_verified":
            if not file_audit.get("files_inspected", 0):
                errors.append(label + "file claim with no files")
            for item in file_audit.get("files", []):
                if not item.get("sha256") or not item.get("byte_size"):
                    errors.append(label + "file verification lacks hash and bytes")
            if not file_audit.get("files"):
                errors.append(label + "file verification lacks file evidence manifest")
        else:
            errors.append(label + "unrecognized raw-file status")

    if errors:
        raise SystemExit("Phase 2 audit validation FAILED:\n - " + "\n - ".join(errors))
    print(f"PASSED: {len(entries)} distinct source-documented resources, "
          f"{actual_file_audits} independently file-verified records.")
    print("Source documentation review must not be described as independent raw data verification.")


if __name__ == "__main__":
    validate()
