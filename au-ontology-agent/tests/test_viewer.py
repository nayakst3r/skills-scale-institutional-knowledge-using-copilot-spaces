"""Runs tests/viewer_check.js against the shipped viewer.

The check exists because two classic <script> blocks once declared the same
top-level const, which throws at parse time and silently kills the second
block. Parsing each block in isolation cannot detect that; only executing
them in one shared context can.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    viewer = ROOT / "viewer" / "bank-ontology.html"
    checker = ROOT / "tests" / "viewer_check.js"
    if not viewer.exists():
        print("viewer not found", file=sys.stderr)
        return 1
    r = subprocess.run(["node", str(checker), str(viewer)],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
