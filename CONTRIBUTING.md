# Contributing to IonSense — Battery Research Dataset Finder

Thank you for helping improve this cross-domain battery research catalogue. It covers EVs **and** stationary storage, laboratory studies, diagnostics, safety, recycling, industrial/portable batteries and specialised applications.

## Propose a record or correction

[Open an issue](https://github.com/SakthiGs/IonSense-Battery-Datasets/issues/new) and include:

- Record title and **original source URL** (ideally a DOI or publisher/repository page).
- Link to the relevant paper or documentation, if available.
- Resource type (raw dataset, publication/source data, code, model weights, synthetic data, etc.).
- The **application domain** if it is supported by the source (EV, stationary, industrial/portable, aerospace, recycling). If not established, leave it blank.
- Research category, tasks (SOH, SOC, RUL, faults, imaging, etc.) and available measurements.
- Chemistry, cell scale, licence and access status **only if verifiable from the source**.
- A short evidence-based description, plus the link supporting each correction.

## Principles

1. Do not equate lithium-ion batteries with EV batteries; distinguish application from research category.
2. Do not infer chemistry or confirmed availability from a title, product model or working URL alone.
3. Credit the dataset publishers and abide by their licences; IonSense only curates links and metadata.
4. Flag possible duplicates instead of deleting records without confirmation.
5. Do not include private information, credentials or copyrighted datasets for redistribution.

To test website changes locally, run `python3 -m http.server 8000` from the repository root and open `http://localhost:8000/docs/`.
