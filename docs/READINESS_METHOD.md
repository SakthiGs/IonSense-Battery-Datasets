# IonSense Data Readiness Passports — methodology (v1)

**Scope:** 106 indexed *resources* in the IonSense catalogue, including datasets, data portals, code, publications and models. A passport exists for each record but does **not** certify that each resource contains an independently downloadable dataset. The v1 passport snapshot was produced on 15 November 2026.

## Purpose

A Data Readiness Passport (DRP) reports what we know, what source documentation supports, what specific cautions exist, and what must be checked before an experiment. It is **not** a numerical dataset quality score, an endorsement of research suitability, a reproducibility certificate, or a licence clearance opinion.

The eight independent dimensions are:

1. **Identity and provenance:** owner, original source, version and cohort identity
2. **Data-file accessibility:** actual file retrieval, credentials and access limitations
3. **Measurements and completeness:** recorded channels, units, time resolution, missingness
4. **Battery chemistry:** documented cell chemistries and cohort variation
5. **Ground-truth labels and tasks:** measured vs derived targets, label definitions and availability
6. **Cohort overlap and independence:** original cell/batch identifiers, portals, derived subsets, split leakage
7. **Licence and reuse rights:** source-specific terms and restrictions
8. **Code and reproducibility:** loaders, canonical splits, code, environment and executed checks

## Evidence vocabulary

| Status | Meaning | Not evidence of |
| --- | --- | --- |
| `source_reviewed` | Original source documentation was previously checked for the specific claim (initially, some chemistry labels). | Downloaded and inspected cell-level files |
| `desk_reviewed` | A documented source-level assessment exists (initially, 13 knee-evidence records). | Replicated experimental ground truth or verified target labels |
| `catalogue_recorded` | A value is present in the existing IonSense catalogue, possibly awaiting independent verification. | Source validation |
| `caution_documented` | A specific source-referenced relationship/risk is flagged. | Proof of duplicate cell samples |
| `not_assessed` | The property is not sufficiently checked. | Evidence that the property is absent or unsuitable |
| `not_applicable` | The question does not apply to this resource type. | Failure |

**Important:** No passport field is marked `file_verified` in v1. All 106 records carry `access_status: not_checked` in the source catalogue. A reachable URL or published paper is **not** evidence that data files were downloaded, reusable, or independently tested.

The initial passports are a **conservative metadata snapshot derived from existing records**, not 106 new primary-source audits. The 58 source-reviewed chemistry entries and 13 desk-reviewed knee entries reuse prior source work, and the three provenance links in `relationships.json` currently affect six record passports. Other unlisted relationships remain unassessed.

## Evidence sources and provenance

- [`datasets.json`](datasets.json): existing descriptions, task tags, signal lists, chemistry review fields, licence strings, original URLs and code URLs
- [`knee_quality.json`](knee_quality.json): existing desk-reviewed knee evidence, label status and methodological cautions; no raw file audits are implied
- [`relationships.json`](relationships.json): curated source and cohort relationships; do not infer cell-level sample duplication from a common host
- [`readiness_passports.json`](readiness_passports.json): machine-readable snapshot of eight dimensions for each record
- [`../scripts/validate_readiness_passports.py`](../scripts/validate_readiness_passports.py): schema, ID coverage, source references and forbidden evidence-level upgrades

## Future field-verification protocol

Every future upgrade from `not_assessed` or `catalogue_recorded` must record at least:

1. **Original source, stable citation and version:** URL/DOI, provider, source date, dataset version, and whether content is data, portal, code, paper or model.
2. **Access observation:** precisely what was tested (landing page vs file download), whether authentication is required, file paths/formats and the checked date; do not redistribute restricted files.
3. **Raw file checks, when permissible:** inspected file manifest, hashes, number of cells/cycles, columns/units, sampling coverage, broken records, missingness and exact processing version.
4. **Target verification:** whether SOH, RUL, fault or knee-onset targets are measured, published as annotations, or derived algorithmically; include methods and uncertainty for derived targets.
5. **Split independence:** cell ID, batch ID, experimental lineage, overlapping cohorts and proposed split grouping; report unverified overlap explicitly.
6. **Licence review:** original terms applying to the actual files rather than only the hosting website.
7. **Reproduction evidence:** executable loader, environment, seed, original versus derived split, checksums and a minimal reproducible check.

A verified result must refer to a **specific field, dataset version and reproducible check**. Simply increasing the number of dataset entries or adding an unsupported aggregate score does not increase readiness.

## Maintenance

Whenever the catalogue gains or removes a record, ensure passport IDs match `datasets.json`. When the source evidence changes, update the affected passport(s), preserve uncertainty, update the `generated_on` field for the new release, and rerun:

```bash
python scripts/validate_readiness_passports.py
```

Dataset users must still cite the **original dataset creators**. IonSense citations are additionally appropriate when its independently documented catalogue or readiness assessments form part of the research methodology.
