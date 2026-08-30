"""MCP server: the only write path into the ontology.

Read tools are free. The write tool (propose_delta) stages a change; it never
applies one. apply_staged runs the gate first and refuses anything that fails.
"""
from __future__ import annotations
import json, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mcp.server.mcpserver import MCPServer
from agent.validator import OntologyValidator
from agent.model import Delta, DeltaKind, Confidence, Provenance, Tier
from agent.proposer import Proposer
from agent.audit import AuditLog
from agent.change_policy import route
from agent.auth import READ_ONLY_TOOLS, WRITE_TOOLS, HUMAN_ONLY_TOOLS, SPEC_REVISION

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "ontology" / "bank-ontology.json"
TTL = ROOT / "ontology" / "bank-ontology.ttl"
SHAPES = ROOT / "ontology" / "shapes.ttl"
STAGED = ROOT / "state" / "staged.jsonl"

server = MCPServer("au-bank-ontology-store")
_model = json.loads(MODEL.read_text())
_audit = AuditLog(ROOT / "state" / "audit.jsonl")
_PM = ROOT / "model" / "model.json"
_phys = json.loads(_PM.read_text()) if _PM.exists() else {"products": [], "counts": {}}
_byclass = {p["classId"]: p for p in _phys.get("products", [])}


def _stamp(payload: dict) -> dict:
    """Provenance in every response - the SEC EDGAR pattern. The model should
    never see a fact without knowing where it came from and how fresh it is."""
    from datetime import datetime, timezone
    return {"source": "au-bank-ontology", "sourceFile": str(MODEL.name),
            "retrievedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "mcpSpecRevision": SPEC_REVISION, "readOnly": True, **payload}


@server.tool()
def describe_ontology() -> dict:
    """Counts, groups and confidence breakdown for the current model."""
    conf = {}
    for sc in _model["scenarios"]:
        conf[sc["validation"]] = conf.get(sc["validation"], 0) + 1
    return {"meta": _model["meta"], "groups": [g["label"] for g in _model["groups"]],
            "confidence": conf}


@server.tool()
def find_class(query: str, limit: int = 20) -> list[dict]:
    """Search classes by label or id."""
    q = query.lower()
    return [c for c in _model["classes"]
            if q in c["label"].lower() or q in c["id"].lower()][:limit]


@server.tool()
def get_scenario(scenario_id: str) -> dict:
    """A scenario with its steps, per-bank applicability and regulatory bundle."""
    for sc in _model["scenarios"]:
        if sc["id"] == scenario_id:
            return sc
    return {"error": f"no scenario {scenario_id}"}


@server.tool()
def scenarios_for_bank(bank: str, status: str = "applicable") -> list[dict]:
    """Which scenarios apply to a given bank. status: applicable |
    appliesWithVariation | notApplicable | unverified."""
    out = []
    for sc in _model["scenarios"]:
        for a in sc["applicability"]:
            if a["bank"].lower() == bank.lower() and a["status"] == status:
                out.append({"id": sc["id"], "label": sc["label"],
                            "category": sc["category"], "note": a["note"]})
    return out


@server.tool()
def scenarios_for_regulator(regulator: str) -> list[dict]:
    """Which scenarios cite a given regulator or instrument."""
    q = regulator.lower()
    return [{"id": sc["id"], "label": sc["label"], "refs": sc["regulatoryReferences"]}
            for sc in _model["scenarios"]
            if any(q in r.lower() for r in sc["regulatoryReferences"])]


@server.tool()
def neighbours(class_id: str) -> dict:
    """Everything one hop from a class, in and out."""
    out, inn = [], []
    for sc in _model["scenarios"]:
        for st in sc["steps"]:
            if st["subject"] == class_id:
                out.append({"predicate": st["predicateLabel"], "object": st["object"],
                            "via": sc["id"]})
            if st["object"] == class_id:
                inn.append({"subject": st["subject"], "predicate": st["predicateLabel"],
                            "via": sc["id"]})
    return {"outgoing": out[:40], "incoming": inn[:40]}


@server.tool()
def unverified_report() -> dict:
    """What the model asserts but nobody has checked. Read this before trusting it."""
    unv = [{"id": s["id"], "label": s["label"], "category": s["category"]}
           for s in _model["scenarios"] if s["validation"] == "notVerified"]
    return {"count": len(unv), "share": round(len(unv) / len(_model["scenarios"]), 2),
            "scenarios": unv}


@server.tool()
def get_attributes(class_id: str) -> dict:
    """The physical shape of a class: columns, types, keys, CDR field mappings,
    APRA reporting dimensions, classification and source system."""
    p = _byclass.get(class_id)
    if not p:
        return {"error": f"no product for class {class_id}"}
    return _stamp({"classId": class_id, "product": p["productId"],
                   "primaryKey": p["primaryKey"], "detail": p["detail"],
                   "confidence": p.get("confidence", "curated"),
                   "warning": ("pattern-generated from group and keyword rules, not sourced; "
                               "confidence notVerified"
                               if p["detail"] != "curated" else None),
                   "attributes": p["attributes"]})


@server.tool()
def find_by_cdr_field(fragment: str) -> list[dict]:
    """Which attributes map to a CDR banking payload field. Use this to check
    whether a CDR change lands anywhere in the model."""
    out = []
    for p in _phys.get("products", []):
        for a in p["attributes"]:
            if a["cdrField"] and fragment.lower() in a["cdrField"].lower():
                out.append({"product": p["productId"], "attribute": a["name"],
                            "cdrField": a["cdrField"]})
    return out


@server.tool()
def find_by_regulatory_dimension(fragment: str) -> list[dict]:
    """Which attributes feed a given APRA form, prudential standard or other
    instrument. Answers 'what breaks if this obligation changes'."""
    out = []
    for p in _phys.get("products", []):
        for a in p["attributes"]:
            if a["efsDimension"] and fragment.lower() in a["efsDimension"].lower():
                out.append({"product": p["productId"], "attribute": a["name"],
                            "dimension": a["efsDimension"],
                            "classification": a["classification"]})
    return out


@server.tool()
def pii_report() -> dict:
    """Every attribute classified pii or sensitive, by product. Privacy Act and
    CPG 235 both need this to exist and be current."""
    rows = []
    for p in _phys.get("products", []):
        for a in p["attributes"]:
            if a["classification"] in ("pii", "sensitive"):
                rows.append({"product": p["productId"], "attribute": a["name"],
                             "classification": a["classification"],
                             "sourceSystem": a["sourceSystem"]})
    return _stamp({"count": len(rows),
                   "products": len({r["product"] for r in rows}), "attributes": rows})


@server.tool()
def attribute_coverage() -> dict:
    """How much of the model is designed versus stubbed. Read this before
    presenting the model as complete."""
    prods = _phys.get("products", [])
    curated = [p for p in prods if p["detail"] == "curated"]
    return _stamp({
        "products": len(prods), "curated": len(curated),
        "patterned": len(prods) - len(curated),
        "curatedShare": round(len(curated) / len(prods), 2) if prods else 0,
        "attributes": _phys.get("counts", {}).get("attributes"),
        "note": "patterned products are generated from group and keyword rules and carry "
                "confidence notVerified; prompts 19-23 in prompts/domains.md replace them",
    })


@server.tool()
def run_gate() -> dict:
    """Run the full validation gate. Nothing merges unless this is open."""
    v = OntologyValidator(str(MODEL), str(TTL), str(SHAPES))
    results = v.run_all()
    return {"open": all(r.passed for r in results),
            "checks": [{"name": r.name, "passed": r.passed, "detail": r.detail,
                        "failures": r.failures} for r in results],
            "confidence": v.confidence_report()}


@server.tool()
def propose_delta(kind: str, target: str, body: dict, source_id: str, tier: int,
                  url: str, rationale: str, confidence: str = "proposed") -> dict:
    """Stage a proposed ontology change. NEVER applies one.

    Returns the routing decision from the change-class policy and writes an
    immutable audit record. An agent calling this cannot approve its own change:
    approval requires a human principal on a separate tool."""
    prov = Provenance.of(source_id, Tier(tier), url, body)
    d = Delta(DeltaKind(kind), target, body, prov, Confidence(confidence), rationale)
    decision = route(kind, body, tier, confidence)

    STAGED.parent.mkdir(parents=True, exist_ok=True)
    with STAGED.open("a") as fh:
        fh.write(json.dumps({**d.to_dict(), "routing": decision}) + "\n")

    _audit.append("propose", f"{source_id}-agent", "agent",
                  {"target": target, "kind": kind, **decision})

    return {"staged": True, "target": target, **decision,
            "turtle": Proposer.to_turtle(d),
            "note": "staged only; approval requires a human principal"}


@server.tool()
def audit_status() -> dict:
    """Chain integrity and segregation-of-duties breaches. This is the evidence
    an auditor or APRA will ask for."""
    return {"chain": _audit.verify(),
            "segregationBreaches": _audit.segregation_breaches(),
            "tolerances": "see governance/tolerance-levels.md"}


@server.tool()
def change_policy() -> dict:
    """The auto-merge versus human-review boundary, and the control each satisfies."""
    from agent.change_policy import ROUTE, CONTROL_MAP, OBLIGATION_MARKERS
    return {"routing": {k.value: v for k, v in ROUTE.items()},
            "controls": CONTROL_MAP,
            "neverAutoMerge": "any change whose body matches an obligation marker",
            "obligationMarkers": list(OBLIGATION_MARKERS)}


@server.tool()
def list_staged() -> list[dict]:
    """Everything waiting, with its routing decision."""
    if not STAGED.exists():
        return []
    return [json.loads(l) for l in STAGED.read_text().splitlines() if l.strip()]


@server.tool()
def applies_on(regulatory_reference: str, on_date: str) -> dict:
    """Was this obligation in force on a given date? Validity is a query,
    not an assumption."""
    hits = [sc for sc in _model["scenarios"]
            if any(regulatory_reference.lower() in r.lower()
                   for r in sc["regulatoryReferences"])]
    return {"reference": regulatory_reference, "on": on_date,
            "note": "validity intervals are populated by the legislation watcher; "
                    "scenarios citing this reference are returned for review",
            "scenarios": [{"id": s["id"], "label": s["label"]} for s in hits]}


if __name__ == "__main__":
    server.run()
