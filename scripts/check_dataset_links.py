"""Weekly check that each dataset's data link still works.

Reads docs/datasets.json, requests every dataset URL and writes
docs/link_status.json. Results:

  ok          the page or file answered normally
  unverified  the site refused automated checks (403, 429, bot protection),
              so the link could not be confirmed either way
  failing     not found, gone, server error, or no response; a dataset is
              only reported as broken after failing two checks in a row

Run: python scripts/check_dataset_links.py
"""
import json
import socket
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

DOCS = Path("docs")
OUT = DOCS / "link_status.json"
TIMEOUT = 25
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; IonSense-link-check/1.0; +https://github.com/SakthiGs/IonSense-Battery-Datasets)",
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
}
BLOCKED = {401, 403, 405, 406, 429, 451}
BOT_WALL = ("anubis", "checking your browser", "captcha", "cf-chl", "access denied")


def check(url):
    """Return (result, http_code, final_url)."""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, headers=HEADERS, method=method)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                code = r.status
                if method == "GET":
                    head = r.read(4096).decode("utf-8", "ignore").lower()
                    if any(w in head for w in BOT_WALL):
                        return "unverified", code, r.geturl()
                return "ok", code, r.geturl()
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (400, 403, 404, 405, 501):
                continue  # some servers reject HEAD; retry with GET
            if e.code in BLOCKED:
                return "unverified", e.code, url
            return "failing", e.code, url
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
            if method == "HEAD":
                continue
            return "failing", None, url
    return "failing", None, url


def main():
    datasets = json.loads((DOCS / "datasets.json").read_text(encoding="utf-8"))
    try:
        previous = json.loads(OUT.read_text(encoding="utf-8")).get("datasets", {})
    except Exception:
        previous = {}
    targets = [(d["id"], d["url"].strip()) for d in datasets if isinstance(d.get("url"), str) and d["url"].strip().startswith("http")]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda t: (t[0], t[1], *check(t[1])), targets))

    today = date.today().isoformat()
    out = {}
    for ds_id, url, result, code, final in results:
        prev = previous.get(ds_id, {})
        fails = prev.get("consecutive_failures", 0) + 1 if result == "failing" else 0
        status = result
        if result == "failing":
            status = "broken" if fails >= 2 else "unverified"
        entry = {
            "url": url,
            "status": status,  # ok | unverified | broken
            "http": code,
            "consecutive_failures": fails,
            "checked": today,
            "last_ok": today if result == "ok" else prev.get("last_ok"),
        }
        if final and final != url:
            entry["redirects_to"] = final
        out[ds_id] = entry

    summary = {s: sum(1 for e in out.values() if e["status"] == s) for s in ("ok", "unverified", "broken")}
    OUT.write_text(json.dumps({
        "updated": today,
        "note": "Weekly automated check of each dataset's data link. 'unverified' means the site blocks automated checks; 'broken' means it failed two checks in a row.",
        "summary": summary,
        "datasets": out,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Checked {len(out)} links: {summary}")


if __name__ == "__main__":
    main()
