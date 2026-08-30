"""The orchestration loop. Watcher -> Differ -> Proposer -> Validator -> route.

Run modes:
  python -m agent.loop --once      one full pass
  python -m agent.loop --cadence daily
Change detection is by payload hash, so a poll that returns identical bytes
costs nothing downstream.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent.differ import Differ
from agent.proposer import Proposer
from agent.validator import OntologyValidator
from agent.model import Tier

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state"
SEEN = STATE / "seen.json"
QUEUE = STATE / "review_queue.jsonl"
LOG = STATE / "run_log.jsonl"


class Watcher:
    """Polls a source and reports only genuine movement."""

    def __init__(self):
        STATE.mkdir(exist_ok=True)
        self.seen = json.loads(SEEN.read_text()) if SEEN.exists() else {}

    def changed(self, source_id: str, payload) -> bool:
        h = hashlib.sha256(json.dumps(payload, sort_keys=True,
                                      default=str).encode()).hexdigest()[:16]
        if self.seen.get(source_id) == h:
            return False
        self.seen[source_id] = h
        SEEN.write_text(json.dumps(self.seen, indent=2))
        return True


class Loop:
    def __init__(self, model_path: Path = ROOT / "ontology" / "bank-ontology.json"):
        self.sources = yaml.safe_load((ROOT / "data" / "sources.yaml").read_text())["sources"]
        self.watcher = Watcher()
        self.differ = Differ(str(model_path))
        self.proposer = Proposer()
        self.model_path = model_path

    def sources_due(self, cadence: str | None) -> list[dict]:
        return [s for s in self.sources
                if cadence is None or s.get("cadence") == cadence]

    def process(self, source_id: str, payload, url: str, brand: str = "") -> dict:
        """One source, one payload. Returns the routing summary."""
        if not self.watcher.changed(source_id, payload):
            return {"source": source_id, "changed": False}

        if source_id == "cdr_products":
            gaps = self.differ.diff_cdr_products(brand, payload, url)
        elif source_id == "cdr_register":
            gaps = self.differ.diff_cdr_brands(payload, url)
        elif source_id == "legislation_register":
            gaps = self.differ.diff_legislation(payload, url)
        else:
            gaps = []

        auto, review = [], []
        for g in gaps:
            d = self.proposer.propose(g)
            if d is None:
                review.append({"gap": g.kind, "subject": g.subject,
                               "reason": "no proposal rule"})
                continue
            record = d.to_dict()
            record["turtle"] = self.proposer.to_turtle(d)
            (auto if d.auto_mergeable() else review).append(record)

        # anything not auto-mergeable goes to a human, with provenance attached
        if review:
            QUEUE.parent.mkdir(exist_ok=True)
            with QUEUE.open("a") as fh:
                for r in review:
                    fh.write(json.dumps(r) + "\n")

        return {"source": source_id, "changed": True, "gaps": len(gaps),
                "autoMerge": len(auto), "humanReview": len(review),
                "deltas": auto}

    def gate(self) -> dict:
        v = OntologyValidator(str(self.model_path),
                              str(ROOT / "ontology" / "bank-ontology.ttl"),
                              str(ROOT / "ontology" / "shapes.ttl"))
        results = v.run_all()
        return {"open": all(r.passed for r in results),
                "checks": [{"name": r.name, "passed": r.passed, "detail": r.detail}
                           for r in results]}

    def run_once(self, fetched: dict[str, tuple] | None = None) -> dict:
        """fetched maps source_id -> (payload, url, brand). In production the
        MCP servers supply this; injected here so the loop is testable offline."""
        started = datetime.now(timezone.utc).isoformat(timespec="seconds")
        outcomes = []
        for sid, (payload, url, brand) in (fetched or {}).items():
            outcomes.append(self.process(sid, payload, url, brand))

        gate = self.gate()
        summary = {"startedAt": started, "outcomes": outcomes, "gate": gate,
                   "merged": gate["open"]}
        LOG.parent.mkdir(exist_ok=True)
        with LOG.open("a") as fh:
            fh.write(json.dumps(summary) + "\n")
        return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--cadence", default=None)
    ap.add_argument("--fixture", default=None, help="JSON file of fetched payloads")
    a = ap.parse_args()
    loop = Loop()
    fetched = {}
    if a.fixture:
        raw = json.loads(Path(a.fixture).read_text())
        fetched = {k: (v["payload"], v["url"], v.get("brand", "")) for k, v in raw.items()}
    out = loop.run_once(fetched)
    print(json.dumps(out, indent=2)[:3000])
    return 0 if out["gate"]["open"] else 1


if __name__ == "__main__":
    sys.exit(main())
