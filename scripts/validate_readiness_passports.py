"""Validate evidence-graded IonSense Data Readiness Passports for every resource.

This validates *metadata integrity only*. It does not certify dataset downloads,
cell-level independence, licence rights, ground truth, or experiment reproducibility.
Run: python scripts/validate_readiness_passports.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FIELDS = (
    "identity", "accessibility", "measurements", "chemistry",
    "labels_and_tasks", "cohort_independence", "licensing", "reproducibility",
)
LEVELS = {
    "source_reviewed", "desk_reviewed", "catalogue_recorded",
    "caution_documented", "not_assessed", "not_applicable",
}


def validate():
    datasets = json.loads((DOCS / "datasets.json").read_text(encoding="utf-8"))
    knee = json.loads((DOCS / "knee_quality.json").read_text(encoding="utf-8"))["records"]
    relations = json.loads((DOCS / "relationships.json").read_text(encoding="utf-8"))["relationships"]
    doc = json.loads((DOCS / "readiness_passports.json").read_text(encoding="utf-8"))
    errors = []
    ids = [d["id"] for d in datasets]
    by_id = {d["id"]: d for d in datasets}
    if len(ids) != len(by_id):
        errors.append("dataset IDs are not unique")
    passports = doc.get("passports")
    if not isinstance(passports, dict):
        raise SystemExit("Missing passports object")
    if doc.get("schema_version") != 1:
        errors.append("Unsupported passport schema version")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(doc.get("generated_on", ""))):
        errors.append("Missing ISO passport generation date")
    if set(passports) != set(ids):
        errors.append(f"Passport ID mismatch: missing={sorted(set(ids)-set(passports))}, "
                      f"unexpected={sorted(set(passports)-set(ids))}")
    if set(doc.get("dimensions", {})) != set(FIELDS):
        errors.append("Eight evidence dimensions are required")
    if set(doc.get("evidence_levels", {})) != LEVELS:
        errors.append("Missing or unexpected evidence levels")

    flagged = {r[key] for r in relations for key in ("a", "b")}
    for id_, passport in passports.items():
        if id_ not in by_id:
            continue
        d = by_id[id_]
        prefix = id_ + ": "
        if passport.get("assessment_scope") != "catalogue_metadata_only":
            errors.append(prefix + "scope must disclose metadata-only status")
        fields = passport.get("dimensions")
        if not isinstance(fields, dict) or set(fields) != set(FIELDS):
            errors.append(prefix + "must contain exactly eight dimensions")
            continue
        for key, item in fields.items():
            level = item.get("status")
            if level not in LEVELS:
                errors.append(prefix + key + " invalid evidence level")
            for text_key in ("finding", "next_check"):
                if not isinstance(item.get(text_key), str) or len(item[text_key].strip()) < 15:
                    errors.append(prefix + key + " missing meaningful " + text_key)
            ref = item.get("evidence_url")
            if ref is not None and (not isinstance(ref, str) or not ref.startswith("https://")):
                errors.append(prefix + key + " non-HTTPS source reference")
            if level in {"source_reviewed", "desk_reviewed", "caution_documented"} and not ref:
                errors.append(prefix + key + " reviewed/caution status lacks a source")
        if fields["accessibility"]["status"] not in {"not_assessed", "not_applicable"} and d.get("access_status") == "not_checked":
            errors.append(prefix + "download status was promoted without a file check")
        if fields["chemistry"]["status"] == "source_reviewed" and d.get("chemistry_verification") != "source_verified":
            errors.append(prefix + "chemistry promoted without reviewed-source metadata")
        if fields["labels_and_tasks"]["status"] == "desk_reviewed" and id_ not in knee:
            errors.append(prefix + "knee status promoted without desk audit")
        if fields["cohort_independence"]["status"] == "caution_documented" and id_ not in flagged:
            errors.append(prefix + "overlap caution has no graph entry")
        if id_ in flagged and fields["cohort_independence"]["status"] != "caution_documented":
            errors.append(prefix + "known relationship was omitted from passport")

    site = (DOCS / "index.html").read_text(encoding="utf-8")
    for marker in (
        "fetch('./readiness_passports.json'", "function readinessPassportSection(d)",
        "function downloadReadinessPassport(d)", "readiness_passport: passportOf(d)",
    ):
        if marker not in site:
            errors.append("Missing dashboard wiring: " + marker)
    if errors:
        raise SystemExit("Readiness passport validation FAILED:\n - " + "\n - ".join(errors))
    statuses = {}
    for p in passports.values():
        for item in p["dimensions"].values():
            statuses[item["status"]] = statuses.get(item["status"], 0) + 1
    print(f"PASSED: {len(passports)} passports / {len(datasets)} resources / "
          f"{len(FIELDS)} dimensions each; evidence counts: {statuses}")
    print("Metadata checks only; zero raw-data file checks implied.")


if __name__ == "__main__":
    validate()
