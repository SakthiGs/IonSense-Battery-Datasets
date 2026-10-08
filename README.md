# IonSense — Battery Research Dataset Finder

![IonSense banner — battery research dataset discovery](battery_banner.svg)

**Discover battery research resources across electric mobility, stationary energy storage, laboratory testing, diagnostics, safety, recycling, and specialised applications.**

[**Explore the Dataset Finder**](https://sakthigs.github.io/IonSense-Battery-Datasets/) · [**Compare datasets**](https://sakthigs.github.io/IonSense-Battery-Datasets/) · [**Coverage view**](https://sakthigs.github.io/IonSense-Battery-Datasets/?view=coverage) · [**Suggest a dataset**](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/new)

## About

IonSense is a **curated discovery catalogue**, not an EV-only dataset collection and not a host of third-party data. It helps researchers locate and compare links to battery datasets and associated research resources, then navigate to the original publishers and authors.

The current index contains **66 entries in 9 research categories**. It covers real-world battery telemetry, experimental cell testing, electrochemical characterisation, imaging, second-life studies, synthetic data and certain related code or model resources. **An indexed record does not automatically mean a downloadable or independently verified dataset.**

## What you can do

- **Discover** resources with text search and faceted filters for **application domain, research category, chemistry, research task, measurements and resource type**.
- **Compare up to three entries** side-by-side using the metadata available, including access status and documentation.
- **Explore coverage** by research task and catalogue category; switch among cards, table, and coverage views.
- **Visit original sources** and linked publications. Source owners retain control of their data and licensing terms.
- **Suggest corrections or new records** through GitHub Issues.

## Application domains vs research categories

**Application domain** describes an explicitly indicated end-use or context such as electric mobility, stationary storage, industrial/portable batteries, aerospace, or second-life and recycling. Many laboratory datasets do not specify a particular application; these remain **Not specified**, not automatically labelled EV. A dataset can relate to multiple application domains when the catalogue description supports them.

**Research category** describes the type or purpose of the record (for example ageing, state estimation, safety, imaging). It is separate from application domain.

### Current catalogue by research category

| Category | Entries |
|---|---:|
| Field & Real-World | 10 |
| Safety & Failure | 5 |
| Lab Aging & Degradation | 23 |
| State Estimation & Health Monitoring | 12 |
| Electrochemical Characterisation | 6 |
| Battery Imaging | 2 |
| Second-Life & Recycling | 2 |
| Aerospace & Specialised | 5 |
| Synthetic & Derived Battery Datasets | 1 |
| **Total** | **66** |

Category counts are for indexed **records**, not confirmed independent datasets or verified downloads. The index can include publications, repositories, code or model resources; potential overlaps and duplicates need source-level review.

## Data and website files

- [`docs/datasets.json`](docs/datasets.json) — structured catalogue and source URLs; metadata may be incomplete or provisional.
- [`docs/index.html`](docs/index.html) — the static GitHub Pages explorer, including filtering, comparison and coverage views.
- [`metadata/`](metadata/) — separate research-oriented quantum-readiness metadata and example tables; do not interpret its scores as experimentally proven quantum advantage.
- [`scripts/check_links.py`](scripts/check_links.py) — link-checking utility; HTTP reachability alone does not establish downloadable data or rights to reuse.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution guidance.

**Running the finder locally:** from the repository root, run `python3 -m http.server 8000` and open `http://localhost:8000/docs/`. GitHub Pages is published from `main /docs`.

## Metadata quality and research cautions

1. **Original sources first.** Read the dataset owner's description, licence, documentation, and associated papers before using or redistributing data. Cite **the original dataset creators**.
2. **Application labels are provisional.** The new application filter is based on information already present in the catalogue; it has **not** been independently verified for all 66 records. Uncertain end-uses are marked **Not specified**.
3. **Chemistry is not guessed.** An unknown cathode chemistry is not inferred merely from lithium-ion or from a battery product name.
4. **Access is not guaranteed.** Links may lead to a paper, software repository or landing page rather than raw measurements. An accessible URL is not proof that a dataset can be downloaded or reused.
5. **Synthetic data is identified as such.** For example, MagBridge-Battery is a synthetic research resource, not an experimental magnetometry recording.
6. **Potential classification conflict:** the indexed “Electric Vehicle Usage Data Set for Battery Aging Studies” entry describes portable 24 V systems. Its application domain is left unassigned pending verification at the original source.

## Contributing

We welcome dataset suggestions, corrections to domain or chemistry labels, source updates, missing licences and documentation, and reports of duplicate or unavailable records. Please [open a GitHub issue](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/new) and include a link supporting the requested change. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licensing and attribution

Repository code is distributed under the terms in [LICENSE](LICENSE) (GNU GPL v3). **Third-party datasets, source material, images, publications and linked resources retain their respective original licences**; this repository licence does not override them. This directory does not rehost the third-party datasets.
