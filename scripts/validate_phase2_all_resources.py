"""Validate every resource in the conservative IonSense Phase 2 audit register.

This checks provenance *bookkeeping* only; it does not fetch or scientifically
validate the original files. Run: python scripts/validate_phase2_all_resources.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REGISTRY = DOCS / "phase2_all_resources.json"
SOURCE_AUDIT = DOCS / "phase2_source_audit_2026-11-15.json"
FILE_EVIDENCE = DOCS / "phase2_file_evidence_2026-11-15.json"


def read(name):
    return json.loads((DOCS / name).read_text(encoding="utf-8"))


def validate():
    datasets = read("datasets.json")
    links = read("link_status.json")
    registry = read("phase2_all_resources.json")
    source = read("phase2_source_audit_2026-11-15.json")
    files = read("phase2_file_evidence_2026-11-15.json")

    errors = []
    by_id = {d["id"]: d for d in datasets}
    ids = set(by_id)
    studied = {e["dataset_id"]: e for e in source["entries"]}
    local = files["cohort_records"]
    records = registry.get("resources")
    if not isinstance(records, dict):
        raise SystemExit("Phase 2 registry missing 'resources' object")

    if registry.get("schema_version") != 1:
        errors.append("Unrecognized schema version")
    if len(datasets) != len(ids):
        errors.append("Duplicate catalogue IDs")
    if set(records) != ids:
        errors.append(
            "Exact catalogue coverage required: missing="
            + repr(sorted(ids - set(records)))
            + ", extra=" + repr(sorted(set(records) - ids))
        )
    if not set(studied) <= ids or not set(local) <= ids:
        errors.append("Source review or local-file evidence not linked to catalogue")
    if set(links.get("datasets", {})) != ids:
        errors.append("Link monitor must cover all resource IDs")
    if files.get("original_provider_checksum_matches_verified") != 0:
        errors.append("Unexpected original-provider checksum verification claim")

    count_link = {"ok": 0, "unverified": 0, "broken": 0}
    for id_, d in by_id.items():
        item = records.get(id_)
        if not isinstance(item, dict):
            continue
        head = id_ + ": "
        if item.get("resource_name") != d.get("name"):
            errors.append(head + "name differs from catalogue")
        if item.get("original_catalogue_url") != d.get("url"):
            errors.append(head + "URL differs from catalogue")
        if item.get("resource_kind") != d.get("source_type"):
            errors.append(head + "resource type differs from catalogue")

        actual_link = links["datasets"][id_]
        monitor = item.get("landing_page_monitor", {})
        status = actual_link.get("status")
        if status not in count_link:
            errors.append(head + "unsupported link monitor status")
        else:
            count_link[status] += 1
        if monitor.get("reachability") != status:
            errors.append(head + "link status does not match live monitor snapshot")
        if monitor.get("checked_on") != actual_link.get("checked", links.get("updated")):
            errors.append(head + "link checked date mismatch")
        if monitor.get("http_status") != actual_link.get("http"):
            errors.append(head + "link HTTP code mismatch")

        doc = item.get("documentation", {})
        should_document = id_ in studied
        if (doc.get("state") == "original_source_described") != should_document:
            errors.append(head + "independent documentation review not backed by source audit")
        if should_document:
            if doc.get("evidence_url") != studied[id_]["source_documentation"]["evidence_url"]:
                errors.append(head + "source audit evidence URL does not match")
            if doc.get("review_ref") != SOURCE_AUDIT.relative_to(ROOT).as_posix():
                errors.append(head + "source review reference invalid")
        else:
            if doc.get("state") != "not_independently_reviewed":
                errors.append(head + "unreviewed source incorrectly promoted")

        local_record = item.get("local_file_inspection", {})
        inspected = id_ in local
        if (local_record.get("state") == "connected_drive_copy_inspected") != inspected:
            errors.append(head + "local inspection not backed by evidence")
        if inspected:
            if local_record.get("evidence_ref") != FILE_EVIDENCE.relative_to(ROOT).as_posix():
                errors.append(head + "local inspection evidence reference invalid")
        elif local_record.get("state") != "not_performed":
            errors.append(head + "unknown local inspection state")

        auth = item.get("publisher_authentication", {})
        if auth.get("state") != "not_verified" or auth.get("matched_original_release_checksum") is not False:
            errors.append(head + "unjustified provider authentication")
        science = item.get("scientific_validation", {})
        expected_science = {
            "task_specific_ground_truth", "original_cell_and_batch_independence",
            "complete_source_file_inventory", "licence_applicability_to_raw_files",
            "runnable_reference_benchmark"
        }
        if set(science) != expected_science or any(v != "not_verified" for v in science.values()):
            errors.append(head + "unsupported scientific validation claim")
        if not item.get("recommended_next_check"):
            errors.append(head + "missing action to complete audit")

    summ = registry.get("summary", {})
    expected = {
        "indexed_resources": len(datasets),
        "full_record_status_coverage": len(records),
        "independently_reviewed_original_source_records": len(studied),
        "documentation_review_pending": len(datasets) - len(studied),
        "resources_with_subsets_of_local_file_bytes_inspected": len(local),
        "local_file_inspection_pending": len(datasets) - len(local),
        "publisher_authenticated_complete_resources": 0,
        "scientifically_validated_for_task": 0,
        "full_phase2_evidence_milestone_completed": False
    }
    for k, v in expected.items():
        if summ.get(k) != v:
            errors.append(f"Summary.{k} should be {v!r}, got {summ.get(k)!r}")
    initial = set(studied)
    actual_local_initial = len(initial & set(local))
    if summ.get("locally_inspected_members_of_initial_15") != actual_local_initial:
        errors.append("Incorrect number of locally inspected initial-pilot resources")
    if summ.get("landing_page_monitor") != {
        "as_of": links.get("updated"),
        "reachable": count_link["ok"],
        "unverified": count_link["unverified"],
        "broken": count_link["broken"]
    }:
        errors.append("Landing monitor summary does not match source data")

    site = (DOCS / "index.html").read_text(encoding="utf-8")
    if "phase2_all_resources.json" not in site:
        errors.append("Dashboard has no Phase 2 all-resource status integration")
    if errors:
        raise SystemExit(
            "PHASE 2 ALL-RESOURCE REGISTRY FAILED:\n - " + "\n - ".join(errors)
        )
    print(f"PASS: {len(records)} / {len(datasets)} resources explicitly tracked.")
    print(f"Source-reviewed: {len(studied)}, local-copy-inspected: {len(local)}, "
          "publisher-authenticated: 0, task-validated: 0.")
    print(f"Landing checks: {count_link} (these are NOT file-access checks).")


if __name__ == "__main__":
    validate()
