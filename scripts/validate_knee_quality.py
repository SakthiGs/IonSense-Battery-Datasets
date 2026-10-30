"""Fail CI when the knee research desk-audit loses provenance or references.
Does not infer, fit, or certify knee-onset ground-truth labels.
Run: python scripts/validate_knee_quality.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "datasets.json"
AUDIT = ROOT / "docs" / "knee_quality.json"

ALLOWED_EVIDENCE = {
    "Published knee-onset study",
    "Published knee-point study",
    "Real-cell knee demonstration",
    "Unlabelled ageing candidate",
    "Aggregated benchmark; knee evidence not audited",
}
MANDATORY = (
    "evidence", "origin", "label_status", "source_review",
    "raw_files_audited", "knee_observed", "capacity_resolution",
    "warning", "research_use", "next_check", "evidence_url", "method_url",
)


def validate():
    datasets = json.loads(DATA.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    errors = []
    if not isinstance(datasets, list):
        raise ValueError("datasets.json must be a list")
    ids = [d.get("id") for d in datasets]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate dataset IDs in datasets.json")
    if audit.get("schema_version") != 1:
        errors.append("Unsupported knee quality schema version")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(audit.get("reviewed_on", ""))):
        errors.append("Missing ISO review date")
    records = audit.get("records")
    if not isinstance(records, dict) or not records:
        errors.append("Knee quality records must be a nonempty object")
        records = {}
    for id_, record in records.items():
        prefix = f"{id_}: "
        if id_ not in ids:
            errors.append(prefix + "not present in datasets.json")
        if not isinstance(record, dict):
            errors.append(prefix + "record must be an object")
            continue
        for key in MANDATORY:
            if key not in record:
                errors.append(prefix + f"missing {key}")
        if record.get("evidence") not in ALLOWED_EVIDENCE:
            errors.append(prefix + "unsupported evidence category")
        if not isinstance(record.get("raw_files_audited"), bool):
            errors.append(prefix + "raw_files_audited must be boolean")
        for key in ("source_review", "label_status", "warning", "research_use",
                    "next_check", "capacity_resolution", "knee_observed", "origin"):
            if not isinstance(record.get(key), str) or not record[key].strip():
                errors.append(prefix + f"{key} must have nonempty text")
        if not str(record.get("evidence_url", "")).startswith("https://"):
            errors.append(prefix + "evidence_url must be HTTPS")
        method = record.get("method_url")
        if not isinstance(method, str) or (method and not method.startswith("https://")):
            errors.append(prefix + "method_url must be HTTPS or empty")
        if record.get("raw_files_audited") is False and record.get("label_status", "").lower().startswith("verified"):
            errors.append(prefix + "cannot claim verified labels when raw data is unaudited")

    site = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    for text in ("knee_quality.json", "kneeEvidenceOf", "Knee-onset research quality"):
        if text not in site:
            errors.append("Dashboard missing knee integration: " + text)
    if errors:
        raise SystemExit("Knee audit checks FAILED:\n - " + "\n - ".join(errors))
    print(f"Knee audit checks passed: {len(records)} evidence-assessed records, "
          f"{len(datasets)} catalogue entries, unique IDs, valid source URLs. "
          "This is metadata validation, not knee-label validation.")


if __name__ == "__main__":
    validate()
