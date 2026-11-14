# Deploying IonSense — Battery Research Dataset Finder

Repository: `https://github.com/SakthiGs/IonSense-Battery-Datasets`
Website: `https://sakthigs.github.io/IonSense-Battery-Datasets/`

GitHub Pages should publish from branch **main**, folder **/docs**. Keep `docs/index.html` and `docs/datasets.json` together.

## Local preview

From the repository root:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/docs/` and verify:

- The README banner reads **106** indexed research resources and **9** research categories, consistent with the 106-entry catalogue.
- The catalogue loads 106 indexed resources and filters by application domain, category, chemistry, research task and measurements.
- Field datasets do not all appear as EV records; check Home Storage, Tsinghua EV and NASA satellite examples.
- Cards, Table, Coverage, Dataset Comparison (up to 3 entries), dark/light mode and copyable comparison URLs still work.
- Cloudflare beacon remains in `docs/index.html` (analytics appears only once deployed, and your dashboard may take time to update).
- New knee-onset research records appear in search results, with source DOI, experimental/synthetic distinction and accurate licence status.
- Bayreuth degradation-mode data and RWTH Aachen EIS data appear under Lab Aging & Degradation, with chemistry NMC, original-source DOI, licence, and no unsupported knee-onset claim.
- Pavan's issue audit is accessible from the README; the audit does not double-count existing MATR/Attia or Sandia study subsets.
- Under the **Research task** facet, choosing **Knee onset** shows 12 curated, evidence-audited research-suitable records; no separate knee-evidence facet appears. Dataset details still show label status, evidence and study caveats. Run `python scripts/validate_knee_quality.py`.
- The navigation, issue and README links open the renamed repository.

## Publish

Commit only the files you intentionally edited. For a future branding/domain pass:

```bash
git add README.md README-DEPLOY.md battery_banner_106.svg docs/index.html docs/datasets.json
git diff --cached --check
git diff --cached --stat
git commit -m "Update IonSense website and documentation"
git push origin main
```

The Git remote should be `https://github.com/SakthiGs/IonSense-Battery-Datasets.git`. The repository's **About** text and any external references must be changed through GitHub independently. Old GitHub Pages paths may not redirect automatically after the repository rename.

## Limitations

Application tags reflect currently catalogued descriptions; they are **not** a complete source-by-source audit. Unknown end-uses remain unclassified; unknown chemistry remains unknown. Some records refer to code/models or publications rather than direct downloads. Do not publish claims that every record has validated access.
