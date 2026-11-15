# IonSense Phase 2 — evidence audit protocol (2026-11-15)

## Purpose and scope

The first pilot contains **15 explicitly named source records**, not 15 certified downloadable datasets. They were selected to represent laboratory ageing, field data, experimental cohorts with known reuse, a hosting portal, direct archives, a synthetic resource, and a derived benchmark. The record-by-record source review is preserved in [phase2_source_audit_2026-11-15.json](../phase2_source_audit_2026-11-15.json).

**Status on 15 November 2026:** 15 source documentation reviews recorded; **0 original raw battery archives independently inspected in this phase**. Several sites disallow automated access, and archives range from megabytes to gigabytes. A source page showing a “Download” button is not a successful download. A provider-published hash is not a hash recomputed by IonSense. Do not promote existing `access_status` or passport evidence levels until each verification actually occurs.

## Evidence and graduation rules

| Tier | Meaning | Evidence required |
|---|---|---|
| A0 — Catalogued | Link and descriptive claims copied into discovery metadata | Catalogue entry; no scientific verification asserted |
| A1 — Source documentation reviewed | Reviewer inspected the original repository, publisher article, or official agency page for the stated facts | Stable source URL, date, exact claim, and provenance |
| A2 — File acquired and integrity checked | A permitted original file was downloaded and parsed | File name, byte length, independently computed SHA-256, publisher checksum comparison where available, extraction errors, and local audit timestamp |
| A3 — Sample/label structure verified | File-level columns, units, missingness and labels tested | Sample counts, cell and batch IDs, label source, sign conventions, repeated measurements, and check scripts |
| A4 — Research-ready for **specified task** | Cell independence, temporal leakage and repeatability demonstrated for the declared protocol | Frozen cell-ID splits, overlap testing, justified task labels, runnable loader and benchmark checks |

Tier A1 **never implies** A2–A4. A source document may describe a dataset that is subsequently unavailable. A4 is task-specific and cannot be inferred from an overall score.

## Required file-level procedure for every resource

1. Follow the **original** source. Verify authors, stable identifier, version and licensing. For a portal or code repository, first identify the exact constituent dataset. Never treat the aggregator as additional independent cells.
2. Retrieve only files that the source author permits us to use; avoid rehosting protected data. Log the URL, retrieval date, HTTP result, name, bytes and computed SHA-256. Keep the source-published MD5/SHA separately from the recomputed value.
3. Without executing arbitrary downloaded code, inspect ZIP member paths, list files, sample CSV or Parquet schemas if supported, check parsing and plausible units. Log invalid files and missing values rather than silently imputing.
4. Extract **exact cell, module, pack and batch identifiers** with source evidence. Identify sequential reuse, standardised copies, overlapping cohorts and retained/excluded cells. Test sample- and cell-level independence of proposed train/validation/test splits.
5. Separate **original measured labels** from algorithmically **derived target values**. In knee-onset research in particular, a published knee point, an onset fitted later, and a ready-made target column are three different claims.
6. Verify the data/metadata licence as applied to the **particular file**, not just the linked software. Check any source-specific attribution conditions.
7. Write a machine-readable result containing evidence, exact test code version, pass/fail/not-assessed for every check, reproducible output and limitations. Only then can a status in `docs/readiness_passports.json` be promoted.

### Phase 2 priority concerns

- **MATR vs closed-loop charging:** both publications point to the same data.matr.io portal. The original publications describe different research questions; shared hosting is not proof of shared cell IDs. Establish exact batch and cell maps.
- **Stanford EV vs Stanford second-life:** the 2024 data article explicitly reports that second-life cells **V4, W8, W9, V5, W10 and G1** were used in the earlier 2022 10-cell EV dataset. Never put the corresponding first- and second-life measurements into nominally independent folds without a defensible longitudinal design. Check IDs in the source files before a released split.
- **Sandia vs Battery Archive:** hosting is not data duplication in the experimental sense, but counting both index entries as independent cohorts is incorrect.
- **BatteryLife and upstream data:** the benchmark redistributes or standardises multiple studies (including XJTU, HUST and Stanford); track derived data lineages separately from original experiments. Its MIT code licence does not transfer rights to all source data.
- **MagBridge-Battery:** the resource explicitly declares a synthetic bridge; it must not be classified as experimentally co-measured magnetometry and degradation ground truth.

## Audit commands and limitations

For file inventory and integrity on **locally downloaded permitted files**:

```bash
python scripts/audit_local_archive.py /path/to/original_dataset.zip --sample-csv-rows 5
python scripts/audit_local_archive.py /path/to/data.csv
```

The script reports SHA-256 and archive structure and samples CSV headers where safe; it **does not** certify scientific validity or independence. Record its JSON output under an audit evidence folder with the source record, version and data provider. Do not commit raw restricted files or sensitive local paths.

Validate this source-review register:

```bash
python scripts/validate_phase2_source_audit.py
```

The CI validator guards against the source-reviewed pilot being mislabeled as a completed file audit. It validates structure and references, not actual third-party data.

## Citation and attribution

Dataset authors receive primary citation credit. IonSense should only be cited when its independently reusable curation or experimental selection methodology is used. This project does not supersede original licences, papers or attribution instructions.
