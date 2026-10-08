# IonSense Dataset Finder — starter release

This is an additive static site for the existing `SakthiGs/EV-Battery-IonSense` repository. It DOES NOT replace the repository README, license or other files.

## Contents
- `docs/index.html` — browser interface, responsive design, search and filters
- `data/datasets.json` — nine initial entries transcribed from existing public README, with original-source URLs
- `.github/workflows/pages.yml` — Pages deployment workflow

## Add to your existing GitHub repository

1. Download and unzip this package on your computer.
2. In a terminal open your local clone of `EV-Battery-IonSense` (the existing repository).
3. Copy the three included directories (`docs`, `data`, `.github`) *into the repository*, merging them with any existing directories; do **not** delete the original repo contents.
4. Run `python3 -m json.tool data/datasets.json >/dev/null` to validate JSON.
5. Run `python3 -m http.server 8000` from the repository root and visit `http://localhost:8000/docs/` to preview.
6. `git add docs/index.html data/datasets.json .github/workflows/pages.yml`
7. `git commit -m "Add IonSense Dataset Finder MVP" && git push origin main`
8. In GitHub **Settings → Pages → Build and deployment**, select **GitHub Actions** as source.
9. Under **Actions**, find `Deploy IonSense Dataset Finder`, run it manually if necessary, then visit `https://sakthigs.github.io/EV-Battery-IonSense/` after the action finishes.

## Scope/limitations
- The current catalogue contains **nine starter entries**, not the full public README catalogue. Expand the JSON after auditing exact links and duplicate entries. The home-storage and portable-system records should not be represented as on-road EV data.
- Dataset links go to original **landing pages**; availability, licenses, signal lists and model suitability need source-by-source verification. No files are hosted by IonSense.
- The site performs **no visitor or outgoing-click tracking**. Add privacy-conscious analytics separately, only if needed.
- The deployment uses the Pages GitHub Actions workflow. GitHub Pages must be enabled and its repository permissions must permit Actions to deploy.
