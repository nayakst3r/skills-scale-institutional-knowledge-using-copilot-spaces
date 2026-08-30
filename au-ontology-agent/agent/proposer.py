"""Turns gaps into deltas. Writes Turtle fragments, never touches the graph directly."""
from __future__ import annotations
from agent.model import Delta, DeltaKind, Confidence, Gap, Validity

GROUP_CLASS = {
    "party": "Party", "role": "PartyRole", "dep": "DepositsAccounts",
    "credit": "CreditSecurity", "mkt": "MarketsWealthService", "prod": "Product",
    "event": "Event", "asset": "AssetSecurity", "place": "LocationChannel",
    "reg": "RegulatoryObject", "ins": "Insurance", "scheme": "SchemesRails",
    "prov": "ProvidersUnderwriters", "body": "RegulatorsBodies", "loy": "LoyaltyRewards",
}


def pascal(s: str) -> str:
    return "".join(w[:1].upper() + w[1:] for w in
                   "".join(c if c.isalnum() else " " for c in s).split())


class Proposer:
    def propose(self, gap: Gap) -> Delta | None:
        s = gap.suggested or {}
        kind = s.get("kind")
        if kind == "addClass":
            return Delta(
                kind=DeltaKind.ADD_CLASS,
                target=pascal(s["label"]),
                body={"label": s["label"], "group": s.get("group", "prod"),
                      "subClassOf": GROUP_CLASS.get(s.get("group", "prod"), "Concept")},
                provenance=gap.provenance,
                confidence=Confidence.PROPOSED,
                rationale=f"{gap.kind}: {gap.detail}",
            )
        if kind == "setValidity":
            return Delta(
                kind=DeltaKind.SET_VALIDITY,
                target=gap.subject,
                body={"regulatoryReference": gap.subject},
                provenance=gap.provenance,
                confidence=Confidence.PROPOSED,
                rationale=gap.detail,
                validity=Validity(start=s.get("commences")),
            )
        return None

    @staticmethod
    def to_turtle(d: Delta) -> str:
        p = d.provenance
        head = (f"### proposed {d.kind.value} | source={p.source_id} tier={int(p.tier)} "
                f"| retrieved={p.retrieved_at} | hash={p.payload_hash}")
        if d.kind is DeltaKind.ADD_CLASS:
            return (f"{head}\n"
                    f'bank:{d.target} a owl:Class ;\n'
                    f'  rdfs:subClassOf bank:{d.body["subClassOf"]} ;\n'
                    f'  rdfs:label "{d.body["label"]}" ;\n'
                    f'  bank:confidence "{d.confidence.value}" ;\n'
                    f'  bank:sourceUrl <{p.url}> ;\n'
                    f'  bank:retrievedAt "{p.retrieved_at}" .\n')
        if d.kind is DeltaKind.SET_VALIDITY:
            v = d.validity or Validity()
            return (f"{head}\n"
                    f'bank:Ref_{abs(hash(d.target)) % 10**8} a bank:RegulatoryReference ;\n'
                    f'  rdfs:label "{d.target[:100]}" ;\n'
                    f'  bank:validFrom "{v.start or "unknown"}" ;\n'
                    f'  bank:confidence "{d.confidence.value}" ;\n'
                    f'  bank:sourceUrl <{p.url}> .\n')
        return f"{head}\n# unhandled delta kind\n"
