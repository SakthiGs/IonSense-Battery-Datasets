"""Validate curated source relationships and dashboard provenance wiring.

This checks referential integrity, not independent-cell identity or raw-data overlap.
Run: python scripts/validate_relationships.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "docs" / "datasets.json"
RELATION_PATH = ROOT / "docs" / "relationships.json"
HTML_PATH = ROOT / "docs" / "index.html"

TYPES = {"shared_portal", "hosted_by", "reported_sequential_cell_reuse"}
STATUSES = {"source_link_verified", "source_description_reviewed"}
REQUIRED = {"a", "b", "type", "label", "status", "description", "evidence_url"}


def validate():
    datasets = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    doc = json.loads(RELATION_PATH.read_text(encoding="utf-8"))
    errors = []
    ids = [d.get("id") for d in datasets]
    if len(ids) != len(set(ids)):
        errors.append("Catalogue contains duplicate IDs")
    if doc.get("schema_version") != 1:
        errors.append("Unsupported relationship schema version")
    if not re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", str(doc.get("reviewed_on", ""))):
        errors.append("Missing relationship review date")
    records = doc.get("relationships")
    if not isinstance(records, list) or not records:
        errors.append("relationships must be a nonempty array")
        records = []

    seen_pairs = set()
    for i, r in enumerate(records):
        prefix = f"relationship[{i}]"
        if not isinstance(r, dict):
            errors.append(prefix + ": must be an object")
            continue
        for key in REQUIRED - set(r):
            errors.append(prefix + f": missing {key}")
        a, b = r.get("a"), r.get("b")
        if a not in ids or b not in ids:
            errors.append(prefix + ": links to a missing dataset ID")
        if a == b:
            errors.append(prefix + ": a dataset cannot relate to itself")
        if isinstance(a, str) and isinstance(b, str):
            pair = tuple(sorted([a, b]))
            if pair in seen_pairs:
                errors.append(prefix + ": duplicate unordered relationship pair")
            seen_pairs.add(pair)
        if r.get("type") not in TYPES:
            errors.append(prefix + ": unsupported relationship type")
        if r.get("status") not in STATUSES:
            errors.append(prefix + ": unsupported provenance status")
        for key in ("label", "description"):
            if not isinstance(r.get(key), str) or len(r[key].strip()) < 12:
                errors.append(prefix + f": {key} too short for review")
        if not str(r.get("evidence_url", "")).startswith("https://"):
            errors.append(prefix + ": evidence_url must be HTTPS")

    site = HTML_PATH.read_text(encoding="utf-8")
    for needle in ("fetch('./relationships.json'", "function relatedRecordsSection(d)",
                   "const overlaps = RELATIONS.filter", "function exportResearchManifest()",
                   "id=\\"export-manifest\\""):
        if needle not in site:
            errors.append("Missing dashboard integration: " + needle)

    if errors:
        raise SystemExit("Relationship checks FAILED:\\n - " + "\\n - ".join(errors))
    print(f"Relationship checks passed: {len(records)} curated links across "
          f"{len(datasets)} catalogue resources. Raw cell overlap is unverified.")


if __name__ == "__main__":
    validate()
