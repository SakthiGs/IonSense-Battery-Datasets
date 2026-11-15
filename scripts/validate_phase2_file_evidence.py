"""Check internal consistency of the Phase 2 locally inspected file evidence.

This verifies the *recorded evidence structure*, NOT the original file bytes.
File-byte audit must be independently rerun where the original copies are available.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SHA = re.compile(r"^[0-9a-f]{64}$")


def validate():
    audit = json.loads((DOCS / "phase2_file_evidence_2026-11-15.json").read_text())
    catalogue = {r["id"] for r in json.loads((DOCS / "datasets.json").read_text())}
    records = audit["cohort_records"]
    errors = []

    if audit.get("schema_version") != 1:
        errors.append("Unsupported schema")
    if set(records) != {
        "nasa-battery-data-set", "osf-battery-magnetometry-archive",
        "magbridge-battery-v1"
    }:
        errors.append("Expected three provenance-specific resource records")
    if set(records) - catalogue:
        errors.append("Audit records missing from catalogue")
    if audit.get("original_provider_checksum_matches_verified", -1) != 0:
        errors.append("Provider checksum claim unsupported")
    mile = audit.get("milestone", {})
    if mile.get("completion_criteria_met") is not False:
        errors.append("Cannot claim the 15-resource milestone is complete")
    if mile.get("publisher_authenticated_raw_data_resources") != 0:
        errors.append("Cannot claim official archive authentication")

    nasa = records["nasa-battery-data-set"]["file_checks"]
    if [f["cell_id"] for f in nasa] != ["B0005", "B0006", "B0007", "B0018"]:
        errors.append("NASA cell file list differs")
    for f in nasa:
        if not SHA.fullmatch(f["sha256_recomputed"]):
            errors.append("NASA SHA-256 missing: " + f["cell_id"])
        if not isinstance(f.get("cycle_types"), dict) or not f["cycle_types"]:
            errors.append("NASA cycle-type counts missing: " + f["cell_id"])
        elif "cycle_count" in f and f["cycle_count"] != sum(f["cycle_types"].values()):
            errors.append("NASA operation counts inconsistent: " + f["cell_id"])
        if f["discharge_capacity_records"] != f["cycle_types"]["discharge"]:
            errors.append("NASA capacity count inconsistent: " + f["cell_id"])
        if f["signal_value_counts"] <= 0:
            errors.append("NASA signal values absent")
    if sum(f["discharge_capacity_records"] for f in nasa) != 636:
        errors.append("NASA discharge total mismatch")
    if records["nasa-battery-data-set"]["summary"]["files_checked"] != len(nasa):
        errors.append("NASA inspected-file count incorrect")

    osf = records["osf-battery-magnetometry-archive"]
    for f in osf["file_checks"]:
        if not SHA.fullmatch(f["sha256_recomputed"]):
            errors.append("OSF SHA-256 missing")
        if f["raw_rows"] != f["time_blocks"] * f["measurements_per_block"]:
            errors.append("OSF run-boundary row mismatch")
        if f["numeric_columns"] != 5:
            errors.append("OSF channel count mismatch")

    m = records["magbridge-battery-v1"]
    for k in ("pulsebat", "osf_input", "staging_manifest"):
        if not SHA.fullmatch(m[k]["sha256_recomputed"]):
            errors.append("MagBridge file or manifest SHA-256 missing: " + k)
    stage = m["staging_manifest"]
    if sum(stage["primary_split"].values()) != stage["claimed_total_rows"]:
        errors.append("Staging primary partition counts mismatch")
    if sum(stage["primary_cell_counts"].values()) != m["pulsebat"]["distinct_physical_cell_ids"]:
        errors.append("Staging primary cell partition counts mismatch")
    if stage["primary_cell_overlap_each_pair"] or stage["primary_sample_id_overlap_each_pair"]:
        errors.append("Primary split contains unexpected reported overlap")
    if stage["record_level_baseline"]["physical_cell_overlap_between_each_pair"] != 56:
        errors.append("Leaky baseline overlap evidence missing")
    if m["official_release_contrast"]["split_counts_match"] is not False:
        errors.append("Official release / staging mismatch must be disclosed")
    if m["parquet_container_checks"]["content_schema_decoded"]:
        errors.append("Cannot claim Parquet row schema was checked")

    site = (DOCS / "index.html").read_text()
    if "phase2_file_evidence_2026-11-15.json" not in site:
        errors.append("Dashboard file evidence wiring absent")
    if errors:
        raise SystemExit("Phase 2 file evidence validation FAILED:\n - " + "\n - ".join(errors))
    print("PASS: 3 local-byte evidence records, 4 NASA MATLAB files, "
          "2 OSF raw text files and MagBridge inputs/staging metadata.")
    print("Publisher authentication remains 0; 15-resource raw-data milestone INCOMPLETE.")


if __name__ == "__main__":
    validate()
