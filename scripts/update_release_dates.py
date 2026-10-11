"""Find when each dataset was first released, from the repository that hosts it.

For every dataset in docs/datasets.json, tries in order:
  1. A manual entry in scripts/release_date_overrides.json (checked by a person)
  2. DataCite, for any data DOI (Zenodo, Mendeley Data, figshare, Dryad, 4TU,
     RADAR, IEEE DataPort, university repositories ...). Uses the earliest of the
     record's Issued/Available dates, its registration date, and the same dates
     on the parent record when the DOI is one version of a series.
  3. figshare API (figshare, Springer Nature, Loughborough and other figshare
     portals): publication date of version 1
  4. OSF API: date the project was created (OSF does not record a release date)
  5. GitHub API: date the repository was created

Writes docs/release_dates.json. Datasets with no date stay out of the file and
show as "Not stated" on the site.

Run: python scripts/update_release_dates.py
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

DOCS = Path("docs")
OUT = DOCS / "release_dates.json"
OVERRIDES = Path("scripts/release_date_overrides.json")
UA = {"User-Agent": "IonSense release-date lookup (https://github.com/SakthiGs/IonSense-Battery-Datasets)"}


def get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 403, 404, 410):
                return None
            time.sleep(3 * (attempt + 1))
        except Exception:
            time.sleep(3 * (attempt + 1))
    return None


def day(s):
    """Normalise '2021', '2021-03', '2021-03-11T10:00:00Z' to the most precise ISO prefix."""
    m = re.match(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", str(s or ""))
    if not m or not (1980 <= int(m.group(1)) <= date.today().year):
        return None
    return "-".join(g for g in m.groups() if g)


def earliest(dates):
    """Earliest date; when two dates share a year, prefer the more precise one."""
    ds = [d for d in dates if d]
    if not ds:
        return None
    first_year = min(d[:4] for d in ds)
    same = [d for d in ds if d[:4] == first_year]
    precise = [d for d in same if len(d) == 10]
    return min(precise) if precise else max(same, key=len)


# ---------- identifiers ----------
def candidate_dois(d):
    out = []
    for f in ("doi", "url"):
        v = d.get(f) or ""
        m = re.search(r"10\.\d{4,9}/[^\s\"<>#?]+", v)
        if m:
            out.append(m.group(0).rstrip("/."))
        m = re.search(r"zenodo\.org/records?/(\d+)", v)
        if m:
            out.append("10.5281/zenodo." + m.group(1))
        m = re.search(r"purl\.stanford\.edu/([a-z0-9]+)", v)
        if m:
            out.append("10.25740/" + m.group(1))
        m = re.search(r"data\.mendeley\.com/datasets/([a-z0-9]+)(?:/(\d+))?", v)
        if m:
            out.append(f"10.17632/{m.group(1)}" + (f".{m.group(2)}" if m.group(2) else ""))
    return list(dict.fromkeys(x.lower() for x in out))


# ---------- sources ----------
def datacite_dates(doi):
    rec = get("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe="/"))
    a = ((rec or {}).get("data") or {}).get("attributes")
    if not a:
        return None, None
    types = {(a.get("types") or {}).get("resourceTypeGeneral", "")}
    dates = [day(x.get("date")) for x in (a.get("dates") or []) if x.get("dateType") in ("Issued", "Available")]
    dates.append(day(a.get("registered")))
    if not any(dates):
        dates.append(day(a.get("publicationYear")))
    parents = [r.get("relatedIdentifier") for r in (a.get("relatedIdentifiers") or [])
               if r.get("relationType") == "IsVersionOf" and r.get("relatedIdentifierType") == "DOI"]
    return dates, (parents, types)


# DOI prefixes of data repositories: records there are data even when typed as "publication".
DATA_PREFIXES = ("10.5281/", "10.17632/", "10.6084/", "10.14459/", "10.18154/", "10.4121/", "10.5287/",
                 "10.25740/", "10.21227/", "10.35097/", "10.5683/", "10.18126/", "10.17630/", "10.1184/", "10.48804/", "10.34810/")


def from_datacite(doi):
    dates, extra = datacite_dates(doi)
    if dates is None:
        return None
    parents, types = extra
    if types & {"Text", "JournalArticle", "ConferencePaper", "Preprint"} and not doi.startswith(DATA_PREFIXES):
        return None  # a paper, not data
    tried = [doi]
    # Version DOIs: the parent (concept) record carries the first release.
    for p in parents:
        pd, _ = datacite_dates(p)
        if pd:
            dates += pd
            tried.append(p)
    # Mendeley Data (10.17632/abc.3) and figshare (10.6084/m9.figshare.123.v2): the DOI without the version
    m = re.match(r"(10\.17632/[a-z0-9]+)\.\d+$", doi) or re.match(r"(.+)\.v\d+$", doi)
    if m and m.group(1) not in tried:
        pd, _ = datacite_dates(m.group(1))
        if pd:
            dates += pd
            tried.append(m.group(1))
    d = earliest(dates)
    return d and {"date": d, "source": "DataCite record for doi:" + tried[-1], "kind": "Released"}


def from_figshare(url):
    m = re.search(r"figshare\.com/.*?/(\d{6,})(?:/\d+)?/?$", url) or re.search(r"(?:figshare\.com|repository\.lboro\.ac\.uk)/articles/[^/]+/[^/]+/(\d{6,})", url)
    if not m:
        return None
    vs = get(f"https://api.figshare.com/v2/articles/{m.group(1)}/versions") or []
    first = next((v for v in vs if v.get("version") == 1), None)
    art = get(first["url"]) if first and first.get("url") else get(f"https://api.figshare.com/v2/articles/{m.group(1)}")
    d = day((art or {}).get("published_date"))
    return d and {"date": d, "source": "figshare record " + m.group(1) + (" (version 1)" if first else ""), "kind": "Released"}


def from_osf(url):
    m = re.search(r"osf\.io/([a-z0-9]{5})", url)
    if not m:
        return None
    node = (get(f"https://api.osf.io/v2/nodes/{m.group(1)}/") or {}).get("data", {}).get("attributes", {})
    d = day(node.get("date_created"))
    return d and {"date": d, "source": "OSF project " + m.group(1), "kind": "Project created"}


def from_github(url):
    m = re.search(r"github\.com/([^/\s]+)/([^/\s#?]+)", url)
    if not m:
        return None
    h = {"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"]} if os.environ.get("GITHUB_TOKEN") else {}
    repo = get(f"https://api.github.com/repos/{m.group(1)}/{m.group(2).removesuffix('.git')}", h) or {}
    d = day(repo.get("created_at"))
    return d and {"date": d, "source": f"GitHub repository {m.group(1)}/{m.group(2)}", "kind": "Repository created"}


def main():
    datasets = json.loads((DOCS / "datasets.json").read_text(encoding="utf-8"))
    try:
        overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")).get("datasets", {})
    except FileNotFoundError:
        overrides = {}
    out, missing = {}, []
    for d in datasets:
        r = None
        if d["id"] in overrides:
            o = overrides[d["id"]]
            r = {"date": o["date"], "source": o["source"], "kind": o.get("kind", "Released"), "checked_by_person": True}
            if o.get("url"):
                r["url"] = o["url"]
        if not r:
            for doi in candidate_dois(d):
                r = from_datacite(doi)
                if r:
                    r["url"] = "https://doi.org/" + r["source"].split("doi:")[1]
                    break
        url = d.get("url") or ""
        if not r and ("figshare" in url or "repository.lboro.ac.uk" in url):
            r = from_figshare(url)
        if not r and "osf.io" in url:
            r = from_osf(url)
        if not r and "github.com" in url:
            r = from_github(url)
        if r:
            out[d["id"]] = r
        else:
            missing.append(d["id"])
        time.sleep(0.3)
    OUT.write_text(json.dumps({
        "updated": date.today().isoformat(),
        "note": "When each dataset was first made public, from the hosting repository. 'Project created' and 'Repository created' are used where the host records no release date.",
        "datasets": dict(sorted(out.items())),
        "not_found": sorted(missing),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Release dates for {len(out)} of {len(datasets)} datasets. Not found: {len(missing)}")
    for m in missing:
        print("  -", m)


if __name__ == "__main__":
    main()
