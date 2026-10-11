"""Fetch citation counts for each dataset's original paper from OpenAlex.

Reads docs/datasets.json and docs/research_uses.json, picks the original
study for each dataset, looks it up on OpenAlex (by DOI, then arXiv DOI,
then exact title) and writes docs/citations.json.

Run: python scripts/update_citations.py
"""
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

DOCS = Path("docs")
API = "https://api.openalex.org/works"
HEADERS = {"User-Agent": "IonSense citation updater (https://github.com/SakthiGs/IonSense-Battery-Datasets)"}


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 * (attempt + 1))
        except Exception:
            time.sleep(2 * (attempt + 1))
    return None


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def by_doi(doi):
    return get(f"{API}/doi:{urllib.parse.quote(doi, safe='/')}?select=id,doi,display_name,cited_by_count")


def by_title(title):
    q = urllib.parse.urlencode({"filter": f"title.search:{title}", "select": "id,doi,display_name,cited_by_count", "per-page": "5"})
    res = get(f"{API}?{q}") or {}
    for w in res.get("results", []):
        if norm(w.get("display_name")) == norm(title):
            return w
    return None


def original_paper(papers):
    ps = [p for p in papers if p.get("relation", "").startswith("Original")]
    ps.sort(key=lambda p: (p["relation"] != "Original study", not p.get("doi")))
    return ps[0] if ps else None


def main():
    datasets = json.loads((DOCS / "datasets.json").read_text(encoding="utf-8"))
    uses = json.loads((DOCS / "research_uses.json").read_text(encoding="utf-8")).get("datasets", {})
    out = {}
    for d in datasets:
        p = original_paper(uses.get(d["id"], {}).get("papers", []))
        if not p:
            continue
        work = None
        if p.get("doi"):
            work = by_doi(p["doi"])
        if not work:
            m = re.search(r"arxiv\.org/abs/([0-9]{4}\.[0-9]{4,5})", p.get("url", "") or p.get("open_access_url", "") or "")
            if m:
                work = by_doi(f"10.48550/arXiv.{m.group(1)}")
        if not work:
            work = by_title(p["title"])
        if work and isinstance(work.get("cited_by_count"), int):
            out[d["id"]] = {"count": work["cited_by_count"], "openalex": work["id"], "title": p["title"]}
        time.sleep(0.2)
    result = {
        "source": "OpenAlex",
        "updated": date.today().isoformat(),
        "note": "Times the dataset's original paper has been cited, according to OpenAlex.",
        "datasets": out,
    }
    (DOCS / "citations.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Citation counts found for {len(out)} datasets.")


if __name__ == "__main__":
    main()
