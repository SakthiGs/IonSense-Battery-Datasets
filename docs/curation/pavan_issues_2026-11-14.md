# Curation review — Pavan's IonSense issues (#10–#20)

Reviewed: **14 November 2026**. GitHub author: [Pxvan09](https://github.com/Pxvan09). Source issues remain open for contributor discussion; this audit does **not** claim that raw files or per-cell knee labels have been reproduced.

| Issue | Suggested source | Catalogue action | Validation / open question |
|---|---|---|---|
| [#10](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/10) | Severson / MIT–Stanford–TRI (MATR) | Already indexed as `early-cycle-life` | Original fast-charge data; verify cohort IDs and knee-onset labels |
| [#11](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/11) | Attia 2020 closed-loop fast charging (45-cell cohort) | Covered by related `closed-loop-fast-charging-optimisation` entry; added overlap warning | Reconstruct exact cell IDs before deciding whether a separate data release is warranted; do not double-count |
| [#12](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/12) | Original research loader code | Linked to the MATR catalogue notes | [Original reproducibility code](https://github.com/rdbraatz/data-driven-prediction-of-battery-cycle-life-before-capacity-degradation) is supporting software, not a new dataset |
| [#13](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/13) | NASA Li-ion Aging | Already indexed as `nasa-battery-data-set` | No source-verified knee-onset events |
| [#14](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/14) | Battery Archive | Already indexed as `battery-archive` | Umbrella portal; its sources must not be re-counted as new independent datasets |
| [#15](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/15) | CALCE | Already indexed as `calce-battery-data` | Data licences and per-cell knee suitability require further checks |
| [#16](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/16) | Samsung INR18650-30Q knee-point ageing | Already indexed as `samsung-inr18650-30q-knee-point-aging` | Knee **point**, not ground-truth **onset**; protocol switches after SOH 80% |
| [#17](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/17) | ISU–ILCC ageing | Already indexed as `isu-ilcc-battery-aging-dataset`; added cell-count caveat | Figshare lists 251 cells; completed/evaluated-cell counts can be lower; verify exact cohort |
| [#18](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/18) | Sandia / Preger | Already indexed as `sandia-commercial-cell-degradation`; mapped to knee audit | 22 selected cells in published NMC analysis are a subset, not a new dataset |
| [#19](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/19) | MATR plus Attia 169-cell cohort | Existing MATR + related Attia records; added explicit non-independence warning | Verify the original cell IDs, exclusions, batch mapping and derived knee labels |
| [#20](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/20) | Hofmann / Sayilgan Bayreuth degradation-mode dataset | **New entry** `bayreuth-three-electrode-degradation-modes-2026` | Official source [DOI 10.57880/rdspace-ubt-54](https://doi.org/10.57880/rdspace-ubt-54): 9 months, 11 checkups, experimental NMC–graphite, 8.29 GB, CC BY-SA 4.0; knee-onset labels **not** confirmed |

## Distinctness and scope

The newly added Bayreuth three-electrode 2026 dataset is **not** the previously indexed `comprehensive-cycle-aging-data-and-analysis-for-commercial-21700-cells` (40 LG M50T cells, published 2024). The first has annotated degradation modes and three-electrode diagnostics; the second is a separate 21700 cycling study.

A curation issue can identify a good dataset without establishing usable labels, file permissions, actual reproducibility, or novel independent samples. In particular, **do not** merge a 124-cell Severson cohort and a 45-cell Attia cohort into a 169-cell benchmark until a cell-level manifest and provenance match are documented.

## Further action

1. Verify independently downloaded per-cell IDs and split definitions for MATR / Attia / Sandia before knee-onset modelling.
2. Inspect Bayreuth raw archive/labels to determine whether some degradation-mode shifts precede observed knee onset; **no knee onset** task tag is applied until evidence supports it.
3. Maintain clear source attribution: issue proposer [Pxvan09](https://github.com/Pxvan09); Bayreuth data creators Hofmann, Sayilgan and colleagues.
