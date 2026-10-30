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

- The catalogue loads 101 indexed resources and filters by application domain, category, chemistry, research task and measurements.
- Field datasets do not all appear as EV records; check Home Storage, Tsinghua EV and NASA satellite examples.
- Cards, Table, Coverage, Dataset Comparison (up to 3 entries), dark/light mode and copyable comparison URLs still work.
- Cloudflare beacon remains in `docs/index.html` (analytics appears only once deployed, and your dashboard may take time to update).
- New knee-onset research records appear in search results, with source DOI, experimental/synthetic distinction and accurate licence status.
- The navigation, issue and README links open the renamed repository.

## Publish

Commit only the files you intentionally edited. For this branding/domain pass:

```bash
git add README.md README-DEPLOY.md battery_banner_96.webp docs/index.html docs/datasets.json
git diff --cached --check
git diff --cached --stat
git commit -m "Update IonSense website and documentation"
git push origin main
```

The Git remote should be `https://github.com/SakthiGs/IonSense-Battery-Datasets.git`. The repository's **About** text and any external references must be changed through GitHub independently. Old GitHub Pages paths may not redirect automatically after the repository rename.

## Limitations

Application tags reflect currently catalogued descriptions; they are **not** a complete source-by-source audit. Unknown end-uses remain unclassified; unknown chemistry remains unknown. Some records refer to code/models or publications rather than direct downloads. Do not publish claims that every record has validated access.
