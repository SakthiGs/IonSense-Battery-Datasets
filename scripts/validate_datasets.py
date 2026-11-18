#!/usr/bin/env python3
"""Validate docs/datasets.json against docs/datasets.schema.json and run integrity checks.

Errors (exit 1):
  - schema violations
  - duplicate ids, duplicate normalised names, duplicate DOIs
  - chemistry_review_status == "source_verified" without an evidence URL
Notes (printed, never fail):
  - several records sharing one landing URL (common for portals such as Battery Archive)
  - how many records lack a license or DOI

Usage:  python scripts/validate_datasets.py [path/to/datasets.json]
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "datasets.json"
SCHEMA = ROOT / "docs" / "datasets.schema.json"


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def main() -> int:
    records = json.loads(DATA.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors, notes = [], []

    for err in sorted(Draft202012Validator(schema).iter_errors(records), key=lambda e: list(e.absolute_path)):
        path = list(err.absolute_path)
        label = records[path[0]].get("id", f"#{path[0]}") if path and isinstance(path[0], int) and path[0] < len(records) else "root"
        errors.append(f"schema: {label}: {'/'.join(map(str, path[1:])) or '(record)'}: {err.message[:160]}")

    seen = {"id": defaultdict(list), "name": defaultdict(list), "doi": defaultdict(list), "url": defaultdict(list)}
    for i, r in enumerate(records):
        rid = r.get("id", f"#{i}")
        seen["id"][r.get("id")].append(rid)
        if r.get("name"):
            seen["name"][norm(r["name"])].append(rid)
        if r.get("doi"):
            seen["doi"][r["doi"].lower()].append(rid)
        if r.get("url"):
            seen["url"][r["url"].rstrip("/")].append(rid)
        if r.get("chemistry_review_status") == "source_verified":
            ev = r.get("chemistry_evidence") or {}
            if not (r.get("chemistry_evidence_url") or ev.get("url")):
                errors.append(f"evidence: {rid}: chemistry is 'source_verified' but no evidence URL is recorded")

    for kind in ("id", "name", "doi"):
        for key, ids in seen[kind].items():
            if key and len(ids) > 1:
                errors.append(f"duplicate {kind}: {key!r} used by {', '.join(ids)}")
    for url, ids in seen["url"].items():
        if len(ids) > 1:
            notes.append(f"shared url: {url} -> {', '.join(ids)}")

    for field in ("license", "doi"):
        missing = [r.get("id", "?") for r in records if not r.get(field)]
        if missing:
            notes.append(f"missing {field}: {len(missing)}/{len(records)} records have no {field} (shown as 'Not specified')")

    for n in notes:
        print("note:", n)
    for e in errors:
        print("ERROR:", e)
    print(f"\n{len(records)} records checked: {len(errors)} error(s), {len(notes)} note(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
