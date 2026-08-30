"""Append-only, hash-chained audit log.

This is the CPS 230 / CPG 235 evidence artefact. Every proposal, approval,
rejection and merge lands here. Tampering breaks the chain and verify() says so.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

GENESIS = "0" * 64


class AuditLog:
    def __init__(self, path: str | Path = "state/audit.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _tip(self) -> str:
        if not self.path.exists():
            return GENESIS
        lines = [l for l in self.path.read_text().splitlines() if l.strip()]
        return json.loads(lines[-1])["hash"] if lines else GENESIS

    def append(self, event: str, actor: str, actor_kind: str, payload: dict,
               decision: str | None = None) -> dict:
        """actor_kind must be 'agent' or 'human'. Segregation of duties depends on it."""
        assert actor_kind in ("agent", "human"), "actor_kind must be agent or human"
        prev = self._tip()
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event": event, "actor": actor, "actorKind": actor_kind,
            "decision": decision, "payload": payload, "prev": prev,
        }
        rec["hash"] = hashlib.sha256(
            json.dumps(rec, sort_keys=True, default=str).encode()).hexdigest()
        with self.path.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        return rec

    def verify(self) -> dict:
        """Walk the chain. Any edit or deletion shows up here."""
        if not self.path.exists():
            return {"valid": True, "records": 0}
        prev, n = GENESIS, 0
        for i, line in enumerate(self.path.read_text().splitlines()):
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec["prev"] != prev:
                return {"valid": False, "brokenAt": i, "reason": "prev hash mismatch"}
            h = rec.pop("hash")
            recomputed = hashlib.sha256(
                json.dumps(rec, sort_keys=True, default=str).encode()).hexdigest()
            if recomputed != h:
                return {"valid": False, "brokenAt": i, "reason": "record altered"}
            prev, n = h, n + 1
        return {"valid": True, "records": n, "tip": prev}

    def segregation_breaches(self) -> list[dict]:
        """An agent may never approve its own proposal. This finds any attempt."""
        proposals, breaches = {}, []
        for line in (self.path.read_text().splitlines() if self.path.exists() else []):
            if not line.strip():
                continue
            r = json.loads(line)
            key = r["payload"].get("target")
            if r["event"] == "propose":
                proposals[key] = r["actor"]
            if r["event"] == "approve":
                if r["actorKind"] != "human":
                    breaches.append({"target": key, "reason": "approver is not human",
                                     "actor": r["actor"]})
                elif proposals.get(key) == r["actor"]:
                    breaches.append({"target": key, "reason": "proposer approved own change",
                                     "actor": r["actor"]})
        return breaches
