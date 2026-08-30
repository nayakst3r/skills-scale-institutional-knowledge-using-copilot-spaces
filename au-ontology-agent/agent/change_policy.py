"""The auto-merge vs human-review boundary, as code.

Risk-based change classes, per the ontology-governance research:
  editorial  - labels, notes, typos                 -> auto-merge
  additive   - new class/property, no semantics lost -> auto-merge if tier 1 + high confidence
  semantic   - domain/range change, re-parenting     -> human review
  breaking   - retire, merge, split, URI change      -> review board
Anything touching an obligation, licence or prudential reference is never auto.
"""
from __future__ import annotations
from enum import Enum
import json


class ChangeClass(str, Enum):
    EDITORIAL = "editorial"
    ADDITIVE = "additive"
    SEMANTIC = "semantic"
    BREAKING = "breaking"


ROUTE = {
    ChangeClass.EDITORIAL: "auto-merge",
    ChangeClass.ADDITIVE: "auto-merge-if-tier1",
    ChangeClass.SEMANTIC: "human-review",
    ChangeClass.BREAKING: "review-board",
}

OBLIGATION_MARKERS = (
    "regulatoryreference", "obligation", "licence", "license", "prudential",
    "accountab", "breach", "designatedservice", "cps 230", "cps 234", "cpg 235",
    "far ", "aps ", "consent", "validity", "validfrom",
)


def classify(kind: str, body: dict) -> ChangeClass:
    if kind in ("retire", "mergeClass", "splitClass", "changeUri"):
        return ChangeClass.BREAKING
    if kind in ("setValidity", "changeDomain", "changeRange", "reparent"):
        return ChangeClass.SEMANTIC
    if kind in ("relabel", "addNote"):
        return ChangeClass.EDITORIAL
    return ChangeClass.ADDITIVE


def route(kind: str, body: dict, tier: int, confidence: str) -> dict:
    cc = classify(kind, body)
    blob = json.dumps(body).lower()
    touches = any(m in blob for m in OBLIGATION_MARKERS)

    if touches:
        decision, why = "human-review", "touches an obligation, licence or validity interval"
    elif cc is ChangeClass.EDITORIAL:
        decision, why = "auto-merge", "editorial only"
    elif cc is ChangeClass.ADDITIVE and tier == 1 and confidence in ("proposed", "validated"):
        decision, why = "auto-merge", "additive change from a tier 1 machine-readable source"
    elif cc is ChangeClass.ADDITIVE:
        decision, why = "human-review", f"additive but source tier {tier}"
    elif cc is ChangeClass.BREAKING:
        decision, why = "review-board", "breaking change to published semantics"
    else:
        decision, why = "human-review", "semantic change"

    return {"changeClass": cc.value, "route": decision, "rationale": why,
            "touchesObligation": touches,
            "control": CONTROL_MAP[decision]}


CONTROL_MAP = {
    "auto-merge":   "CPG 235 data quality controls; logged to immutable audit",
    "human-review": "CPS 220 three lines of defence; segregation of duties; FAR accountable person",
    "review-board": "CPS 230 change management; board-approved tolerance; independent assurance",
}
