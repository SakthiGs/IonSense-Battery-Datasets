"""Build docs/whats_new.json: what was added to IonSense, and when.

Reads the git history of docs/datasets.json and docs/research_uses.json to find
the day each dataset and each "Used in research" study first appeared. The
first version of each file is the starting catalogue and is not reported as new.
Feature announcements come from scripts/whats_new_notes.json (written by hand).

Needs the full history: in GitHub Actions use actions/checkout with fetch-depth: 0.
Run: python scripts/build_whats_new.py
"""
import json
import re
import subprocess
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

DOCS = Path("docs")
OUT = DOCS / "whats_new.json"
NOTES = Path("scripts/whats_new_notes.json")
KEEP_DAYS = 120   # events older than this drop off the strip
NEW_BADGE_DAYS = 30


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def history(path):
    """Yield (day, parsed JSON) for every commit that changed `path`, oldest first."""
    for line in git("log", "--reverse", "--format=%H %cs", "--", path).splitlines():
        sha, day = line.split()
        try:
            yield day, json.loads(git("show", f"{sha}:{path}"))
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            continue


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def main():
    current = json.loads((DOCS / "datasets.json").read_text(encoding="utf-8"))
    names = {d["id"]: d["name"] for d in current}

    # Datasets: first day each id appeared after launch day (everything on the first day is the starting catalogue).
    added_ds, seen, launch = {}, set(), None
    for day, data in history("docs/datasets.json"):
        ids = {d.get("id") for d in data if isinstance(d, dict) and d.get("id")}
        launch = launch or day
        if day != launch:
            for i in ids - seen:
                added_ds.setdefault(i, day)
        seen |= ids

    # Studies: first day each (dataset, title) pair appeared after the file's first version.
    added_st, seen, first = {}, set(), True
    for day, doc in history("docs/research_uses.json"):
        pairs = {}
        for ds_id, entry in (doc.get("datasets") or {}).items():
            for p in entry.get("papers", []):
                if p.get("title"):
                    pairs[(ds_id, norm(p["title"]))] = p
        if not first:
            for k in pairs.keys() - seen:
                added_st.setdefault(k, (day, pairs[k]))
        seen |= pairs.keys()
        first = False

    cutoff = (date.today() - timedelta(days=KEEP_DAYS)).isoformat()
    events = []

    by_day = defaultdict(list)
    for i, day in added_ds.items():
        if i in names and day >= cutoff:
            by_day[day].append({"id": i, "name": names[i]})
    for day, items in by_day.items():
        events.append({"date": day, "type": "datasets", "items": sorted(items, key=lambda x: x["name"])})

    # Group new studies by day and by paper (one paper often covers several datasets).
    by_day = defaultdict(lambda: defaultdict(lambda: {"datasets": []}))
    for (ds_id, t), (day, p) in added_st.items():
        if ds_id not in names or day < cutoff:
            continue
        g = by_day[day][t]
        g.update(title=p["title"], year=p.get("year"), authors=p.get("authors", ""), pinned=p.get("pinned") is True)
        g["datasets"].append({"id": ds_id, "name": names[ds_id]})
    for day, papers in by_day.items():
        items = sorted(papers.values(), key=lambda x: (-len(x["datasets"]), x["title"]))
        events.append({"date": day, "type": "studies", "items": items})

    try:
        notes = json.loads(NOTES.read_text(encoding="utf-8")).get("notes", [])
    except FileNotFoundError:
        notes = []
    for n in notes:
        if n.get("date", "") >= cutoff:
            events.append({"date": n["date"], "type": "note", "text": n["text"], "link": n.get("link", "")})

    order = {"datasets": 0, "studies": 1, "note": 2}  # within a day: data first, then feature notes
    events.sort(key=lambda e: order[e["type"]])
    events.sort(key=lambda e: e["date"], reverse=True)
    badge_cutoff = (date.today() - timedelta(days=NEW_BADGE_DAYS)).isoformat()
    OUT.write_text(json.dumps({
        "updated": date.today().isoformat(),
        "note": "Datasets and studies added to IonSense, by the day they first appeared in the catalogue.",
        "new_datasets": {i: d for i, d in sorted(added_ds.items()) if i in names and d >= badge_cutoff},
        "events": events,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(events)} events; {len(added_ds)} datasets and {len(added_st)} studies added since launch.")


if __name__ == "__main__":
    main()
