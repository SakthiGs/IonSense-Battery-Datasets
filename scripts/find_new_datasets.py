"""Weekly search for new public battery datasets.

Looks for battery datasets registered since the last run and for new data
papers, drops anything already in docs/datasets.json or already reported,
and writes a Markdown list of candidates for a person to review.
Nothing is added to the catalogue automatically.

Sources
  DataCite  dataset DOIs from Zenodo, Mendeley Data, figshare, Dryad,
            IEEE DataPort, 4TU, RADAR, university repositories and others
  OpenAlex  new papers in Scientific Data and Data in Brief, plus any paper
            whose title says it releases a battery dataset

Run: python scripts/find_new_datasets.py
Writes scripts/finder_seen.json (memory between runs) and
finder_report.md (issue body; empty when there is nothing new).
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

DOCS = Path("docs")
STATE = Path("scripts/finder_seen.json")
REPORT = Path("finder_report.md")
UA = {"User-Agent": "IonSense dataset finder (https://github.com/SakthiGs/IonSense-Battery-Datasets)"}
FIRST_RUN_DAYS = 35
MAX_REPORTED = 40

BATTERY = re.compile(r"\b(batter(y|ies)|li-?ion|lithium[- ]ion|sodium[- ]ion|na-?ion|zinc[- ]ion|lifepo4|lfp|nmc|nca|lco|cathode|anode|electrolyte|cell[- ]level)\b", re.I)
MUST = re.compile(r"\b(batter(y|ies)|li-?ion|lithium[- ]ion|sodium[- ]ion|zinc[- ]ion)\b", re.I)
TOPIC = re.compile(r"\b(ag(e)?ing|degradation|cycl(e|ing)|state[- ]of[- ](health|charge)|soh|soc|rul|remaining useful|capacity|impedance|eis|thermal runaway|charging|discharg|calendar|second[- ]life|retired|recycl|fault|diagnos|prognos|electric vehicle|\bev\b|field data|fleet|energy storage|pack|module)\b", re.I)
DATA_WORDS = re.compile(r"\b(data ?set|data descriptor|database|benchmark|open data|data release|measurement data|test data|raw data)\b", re.I)
NOT_BATTERY = re.compile(r"(\btest battery|\bcognitive|neuropsycholog|questionnaire|assessment battery|battery of (tests|assays)|artillery|battery cage|\bhens?\b|battery-free|search intelligence|logistics 20\d\d|ontology)", re.I)
# Beam-time records from large facilities describe experiments, not released data.
SKIP_PUBLISHERS = re.compile(r"synchrotron|isis facility|neutron source|diamond light", re.I)
SOURCE_DATA_ONLY = re.compile(r"^(source data|supplementary|supporting (data|information)|data for figure|figure \d)", re.I)


def get(url):
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                print(f"  {e.code} for {url[:120]}")
                return None
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f"  retry after {type(e).__name__}")
            time.sleep(5 * (attempt + 1))
    return None


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def bare_doi(s):
    m = re.search(r"10\.\d{4,9}/[^\s\"'<>#?]+", s or "")
    return m.group(0).rstrip(".").lower() if m else ""


def known_items():
    data = json.loads((DOCS / "datasets.json").read_text(encoding="utf-8"))
    dois, urls, titles = set(), set(), set()
    for d in data:
        for f in ("doi", "url", "paper", "paper_url", "chemistry_evidence_url"):
            v = d.get(f) or ""
            if bare_doi(v):
                dois.add(bare_doi(v))
            if v.startswith("http"):
                urls.add(v.rstrip("/").lower())
        titles.add(norm(d.get("name")))
        titles.update(norm(a) for a in d.get("aka", []) if len(a) > 12)
    try:
        uses = json.loads((DOCS / "research_uses.json").read_text(encoding="utf-8"))
        for entry in uses.get("datasets", {}).values():
            for p in entry.get("papers", []):
                if p.get("doi"):
                    dois.add(p["doi"].lower())
                titles.add(norm(p.get("title")))
    except FileNotFoundError:
        pass
    return dois, urls, titles


def score(title, desc=""):
    """Rough relevance: 0 means skip."""
    text = f"{title} {desc}"
    if NOT_BATTERY.search(text) or not MUST.search(title + " " + desc[:400]):
        return 0
    s = 2 if MUST.search(title) else 1
    s += min(len(TOPIC.findall(text)), 4)
    s += 2 if DATA_WORDS.search(title) else 0
    s += 1 if BATTERY.search(title) else 0
    return s


def from_datacite(since):
    """Dataset DOIs registered since `since` whose title mentions batteries."""
    q = ('titles.title:(battery OR batteries OR "lithium-ion" OR "li-ion" OR "sodium-ion") '
         f'AND registered:[{since} TO *]')
    out, url = [], "https://api.datacite.org/dois?" + urllib.parse.urlencode({
        "query": q, "resource-type-id": "dataset", "page[size]": "200",
        "fields[dois]": "titles,creators,publisher,publicationYear,descriptions,url,registered,relatedIdentifiers,types"})
    for _ in range(5):  # at most 1,000 records a week
        res = get(url)
        if not res:
            break
        for rec in res.get("data", []):
            a = rec.get("attributes", {})
            title = ((a.get("titles") or [{}])[0].get("title") or "").strip()
            desc = " ".join((x.get("description") or "") for x in (a.get("descriptions") or []))[:1500]
            rel = a.get("relatedIdentifiers") or []
            # Zenodo and figshare register one DOI per version; keep only the concept record when we can tell.
            if any(r.get("relationType") == "IsVersionOf" for r in rel):
                continue
            out.append({
                "kind": "Dataset",
                "title": title,
                "doi": rec.get("id", "").lower(),
                "url": f"https://doi.org/{rec.get('id')}",
                "landing": a.get("url") or "",
                "publisher": (a.get("publisher") or "") if isinstance(a.get("publisher"), str) else (a.get("publisher") or {}).get("name", ""),
                "year": a.get("publicationYear"),
                "date": (a.get("registered") or "")[:10],
                "creators": [c.get("name", "") for c in (a.get("creators") or [])][:3],
                "n_creators": len(a.get("creators") or []),
                "desc": re.sub(r"<[^>]+>", " ", desc),
            })
        url = (res.get("links") or {}).get("next")
        if not url:
            break
        time.sleep(1)
    return out


def from_openalex(since):
    """New data papers (Scientific Data, Data in Brief) and papers that say they release battery data."""
    base = "https://api.openalex.org/works?"
    sel = "id,doi,display_name,publication_date,authorships,primary_location"
    queries = [
        f"primary_location.source.issn:2052-4463|2352-3409,from_publication_date:{since},title.search:battery|batteries|lithium-ion",
        f"from_publication_date:{since},title.search:battery dataset|battery data set|battery database|battery benchmark",
    ]
    out = []
    for f in queries:
        url = base + urllib.parse.urlencode({"filter": f, "select": sel, "per-page": "100"})
        res = get(url) or {}
        for w in res.get("results", []):
            title = (w.get("display_name") or "").strip()
            src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
            data_journal = src in ("Scientific Data", "Data in Brief")
            if not data_journal and not DATA_WORDS.search(title):
                continue
            auth = [a.get("author", {}).get("display_name", "") for a in (w.get("authorships") or [])]
            out.append({
                "kind": "Data paper" if data_journal else "Paper releasing data",
                "title": title,
                "doi": bare_doi(w.get("doi") or ""),
                "url": w.get("doi") or w.get("id"),
                "landing": "",
                "publisher": src,
                "year": (w.get("publication_date") or "")[:4],
                "date": w.get("publication_date") or "",
                "creators": auth[:3],
                "n_creators": len(auth),
                "desc": "",
            })
        time.sleep(1)
    return out


def main():
    today = date.today()
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        state = {}
    seen = state.get("seen", {})
    last = state.get("last_run")
    since = (date.fromisoformat(last) - timedelta(days=3)) if last else today - timedelta(days=FIRST_RUN_DAYS)
    since = since.isoformat()
    print(f"Searching for items since {since}")

    dois, urls, titles = known_items()
    found = from_datacite(since) + from_openalex(since)
    print(f"Fetched {len(found)} records")

    by_title = {}
    for c in found:
        key = c["doi"] or norm(c["title"])
        t = norm(c["title"])
        if not c["title"] or key in seen or c["doi"] in dois or t in titles or c["landing"].rstrip("/").lower() in urls:
            continue
        if SOURCE_DATA_ONLY.search(c["title"]) or SKIP_PUBLISHERS.search(c["publisher"] or ""):
            continue
        if not (TOPIC.search(c["title"]) or DATA_WORDS.search(c["title"])):
            continue  # the title should say what kind of battery data it is
        s = score(c["title"], c["desc"])
        if s < 3:
            continue
        c["score"] = s
        # collapse duplicates (same title from several versions or sources)
        if t in by_title and by_title[t]["score"] >= s:
            continue
        by_title[t] = c
    fresh = sorted(by_title.values(), key=lambda c: c["date"], reverse=True)  # newest first...
    fresh.sort(key=lambda c: -c["score"])  # ...within each relevance level
    report = fresh[:MAX_REPORTED]

    for c in fresh:  # remember everything we looked at, so it is not reported twice
        seen[c["doi"] or norm(c["title"])] = today.isoformat()
    # keep the memory file small: forget items older than two years
    cutoff = (today - timedelta(days=730)).isoformat()
    seen = {k: v for k, v in seen.items() if v >= cutoff}
    STATE.write_text(json.dumps({"last_run": today.isoformat(), "seen": dict(sorted(seen.items()))}, indent=1) + "\n", encoding="utf-8")

    if not report:
        REPORT.write_text("", encoding="utf-8")
        print("No new candidates.")
        return

    lines = [
        f"The weekly search found **{len(fresh)} possible new battery datasets** published or registered since {since}"
        + (f" (showing the {MAX_REPORTED} most relevant)" if len(fresh) > MAX_REPORTED else "") + ".",
        "",
        "None of these have been added. Tick the ones worth adding, then ask Claude to verify and add the ticked items "
        "(chemistry, scale, licence and original paper are checked at source before anything goes on the site).",
        "",
    ]
    for kind in ("Dataset", "Data paper", "Paper releasing data"):
        group = [c for c in report if c["kind"] == kind]
        if not group:
            continue
        lines += [f"### {kind}s" if kind != "Paper releasing data" else "### Papers that say they release data", ""]
        for c in group:
            who = ", ".join(x for x in c["creators"] if x)
            if c["n_creators"] > 3:
                who += " et al."
            meta = " · ".join(x for x in [who, c["publisher"], c["date"]] if x)
            lines.append(f"- [ ] [{c['title']}]({c['url']})  \n  {meta}")
        lines.append("")
    lines.append("<sub>Generated by scripts/find_new_datasets.py from DataCite and OpenAlex. Items listed here will not be listed again.</sub>")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Reported {len(report)} candidates.")


if __name__ == "__main__":
    main()
