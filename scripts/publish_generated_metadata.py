"""Safely publish generated IonSense metadata when other commits reach main.

Usage:
  python scripts/publish_generated_metadata.py \
      docs/whats_new.json "Update what's new" scripts/build_whats_new.py

The generator has already run once in a preceding workflow step. If another
writer moves main before the push, fetch the latest main, discard ONLY the
temporary GitHub Actions checkout, rerun the generator, then retry. Never
force-push or resolve generated JSON conflicts by selecting stale content.
"""
import subprocess
import sys
import time
from pathlib import Path

MAX_ATTEMPTS = 5


def run(*args, check=True):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.stdout.strip():
        print(p.stdout.rstrip(), flush=True)
    if p.stderr.strip():
        print(p.stderr.rstrip(), file=sys.stderr, flush=True)
    if check and p.returncode:
        raise RuntimeError(f"{' '.join(args)} exited with status {p.returncode}")
    return p


def main():
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: publish_generated_metadata.py OUTPUT MESSAGE GENERATOR_SCRIPT"
        )
    output, message, script = sys.argv[1:]
    if output not in ("docs/whats_new.json", "docs/release_dates.json"):
        raise SystemExit("Refusing to publish an unexpected output path.")
    if script not in ("scripts/build_whats_new.py", "scripts/update_release_dates.py"):
        raise SystemExit("Refusing to run an unexpected generator.")
    if not Path(output).is_file():
        raise SystemExit(f"Generated output missing: {output}")

    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"Publish {output}: attempt {attempt}/{MAX_ATTEMPTS}", flush=True)
        if attempt > 1:
            # A concurrent writer advanced main. Regenerate from its actual
            # content instead of rebasing a possibly conflicting JSON snapshot.
            run("git", "fetch", "origin",
                "+refs/heads/main:refs/remotes/origin/main")
            run("git", "reset", "--hard", "refs/remotes/origin/main")
            run(sys.executable, script)

        run("git", "add", "--", output)
        changed = run("git", "diff", "--cached", "--quiet", check=False)
        if changed.returncode == 0:
            print(f"No changes to publish in {output}.", flush=True)
            return
        if changed.returncode != 1:
            raise RuntimeError("git diff --cached failed.")

        run("git", "commit", "-m", message)
        pushed = run("git", "push", "origin", "HEAD:refs/heads/main", check=False)
        if pushed.returncode == 0:
            print(f"Published {output}.", flush=True)
            return
        if attempt < MAX_ATTEMPTS:
            print("main moved or push was rejected; rebuilding on current main.",
                  flush=True)
            time.sleep(min(attempt * 2, 8))

    raise SystemExit(
        f"Failed to publish {output} after {MAX_ATTEMPTS} attempts. "
        "No force push attempted."
    )


if __name__ == "__main__":
    main()
