"""Offline inventory and checksum tool for ORIGINAL, locally permitted data files.

This tool does not download files, execute provider code, or certify scientific
suitability. Use together with docs/curation/PHASE2_AUDIT_PROTOCOL.md.

Usage:
  python scripts/audit_local_archive.py path/to/original.zip --sample-csv-rows 5
  python scripts/audit_local_archive.py path/to/data.csv --output /tmp/inventory.json
"""
import argparse
import csv
import hashlib
import io
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

MAX_SAMPLE_UNCOMPRESSED_BYTES = 2 * 1024 * 1024
MAX_ZIP_ENTRIES = 100000


def hash_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_sample(stream, max_rows):
    with io.TextIOWrapper(stream, encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = [r for _, r in zip(range(max_rows), reader)]
    return {"header": header, "row_count_sampled": len(rows), "sample_rows": rows}


def inspect(path, sample_rows):
    p = Path(path)
    if not p.is_file():
        raise ValueError("The supplied path is not a file")
    result = {
        "tool": "ionsense-file-inventory-v1",
        "checked_on_utc": datetime.now(timezone.utc).isoformat(),
        "filename": p.name,
        "byte_size": p.stat().st_size,
        "sha256_recomputed": hash_file(p),
        "source_url": None,
        "publisher_checksum_compared": False,
        "sample_labels_verified": False,
        "cell_independence_verified": False,
        "warnings": [
            "This is a local integrity/structure inventory, not an experimental scientific audit."
        ],
    }
    ext = p.suffix.lower()
    if ext == ".zip":
        listing = []
        with zipfile.ZipFile(p, "r") as z:
            infos = z.infolist()
            if len(infos) > MAX_ZIP_ENTRIES:
                raise ValueError("Archive member count exceeds conservative safety cap")
            for entry in infos:
                name = entry.filename
                segments = name.replace("\\", "/").split("/")
                unsafe = name.startswith("/") or ".." in segments or (
                    segments and ":" in segments[0]
                )
                record = {
                    "filename": name,
                    "uncompressed_bytes": entry.file_size,
                    "compressed_bytes": entry.compress_size,
                    "crc32_from_zip_header": f"{entry.CRC:08x}",
                    "unsafe_path": bool(unsafe),
                }
                if unsafe:
                    result["warnings"].append("Potentially unsafe ZIP path: " + name)
                if name.lower().endswith(".csv") and not unsafe:
                    if 0 < entry.file_size <= MAX_SAMPLE_UNCOMPRESSED_BYTES:
                        try:
                            with z.open(entry, "r") as stream:
                                record["csv_sample"] = csv_sample(stream, sample_rows)
                        except Exception as exc:
                            record["sample_error"] = str(exc)[:160]
                    else:
                        record["sample_not_read"] = "CSV member exceeds safe preview limit"
                listing.append(record)
        result["format"] = "zip"
        result["archive_entries"] = listing
        result["archive_member_count"] = len(listing)
        result["crc_integrity_test_performed"] = False
    elif ext == ".csv":
        with p.open("rb") as stream:
            result["csv_sample"] = csv_sample(stream, sample_rows)
        result["format"] = "csv"
    else:
        result["format"] = ext.removeprefix(".") or "unknown"
        result["warnings"].append(
            "Only hash and file size examined; no schema parser for this format"
        )
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", help="Existing permitted original data file on your computer")
    p.add_argument("--sample-csv-rows", type=int, default=5)
    p.add_argument("--output", help="Optional JSON report path; avoid committing private file paths")
    args = p.parse_args()
    if not 0 <= args.sample_csv_rows <= 20:
        p.error("--sample-csv-rows must be between 0 and 20")
    try:
        report = inspect(args.file, args.sample_csv_rows)
    except (OSError, zipfile.BadZipFile, ValueError) as e:
        p.exit(1, f"Audit failed: {e}\n")
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
