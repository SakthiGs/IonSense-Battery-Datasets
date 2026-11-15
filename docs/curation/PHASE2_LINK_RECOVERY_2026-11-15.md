# Phase 2 — source-link recovery candidates (15 November 2026)

The historical link monitor reports 2 records as **broken**. These flags are not proof that the datasets are permanently inaccessible, and this document does not change original-file verification status.

## battery-failure-databank-nrel

- Existing catalogue link: https://www.nrel.gov/transportation/battery-failure.html
- Official replacement candidate: https://www.nlr.gov/transportation/battery-failure
- Evidence: the old institutional page redirects to the National Laboratory of the Rockies site. The new official page describes the Battery Failure Databank and includes a spreadsheet download link.
- Verification needed: check the canonical page on GitHub Actions, retrieve provider spreadsheet metadata under applicable conditions, record actual file identity and SHA-256, and then update the catalogue URL and the link monitor. Do **not** treat a redirect as proof that the spreadsheet itself was downloaded.
- Reference: https://www.nlr.gov/transportation/battery-failure

## bayreuth-three-electrode-degradation-modes-2026

- Existing catalogue link: https://rdspace.uni-bayreuth.de/entities/researchdata/0bb95cc2-8ce9-4dcb-b7c0-4eda5949f9ed
- Official persistent-identifier candidates: https://doi.org/10.57880/rdspace-ubt-54 and https://rdspace.uni-bayreuth.de/handle/rdspace-ubt/963
- Evidence: University of Bayreuth's RDSpace metadata lists the dataset and persistent identifier, including NMC/graphite three-electrode ageing measurements and a CC BY-SA 4.0 metadata licence.
- Verification needed: retry original portal access and DOI resolution, inspect its downloadable archive and hash metadata, and check that any mirrored copy is the same version. A bot-blocked URL must not be misrepresented as permanently unavailable.
- Reference: https://rdspace.uni-bayreuth.de/entities/researchdata/0bb95cc2-8ce9-4dcb-b7c0-4eda5949f9ed/full

No source URL or `access_status` is automatically promoted based on these recovery candidates; the Phase 2 register is a dated snapshot and must preserve what the monitor actually observed.
