"""Core types. Provenance and confidence are mandatory on every fact."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Optional
import hashlib, json


class Tier(int, Enum):
    AUTHORITATIVE_STRUCTURED = 1   # agent may assert
    AUTHORITATIVE_UNSTRUCTURED = 2 # agent proposes, human reviews
    BANK_PUBLISHED = 3             # agent proposes, human reviews
    SECONDARY = 4                  # detection only


class Confidence(str, Enum):
    VALIDATED = "validated"
    CORRECTED = "corrected"
    NOT_VERIFIED = "notVerified"
    PROPOSED = "proposed"


class DeltaKind(str, Enum):
    ADD_CLASS = "addClass"
    ADD_PROPERTY = "addProperty"
    ADD_SCENARIO = "addScenario"
    SET_VALIDITY = "setValidity"
    UPDATE_APPLICABILITY = "updateApplicability"
    RETIRE = "retire"


@dataclass
class Provenance:
    source_id: str
    tier: Tier
    url: str
    retrieved_at: str
    payload_hash: str

    @staticmethod
    def of(source_id: str, tier: Tier, url: str, payload: Any) -> "Provenance":
        blob = json.dumps(payload, sort_keys=True, default=str).encode()
        return Provenance(
            source_id=source_id, tier=Tier(tier), url=url,
            retrieved_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            payload_hash=hashlib.sha256(blob).hexdigest()[:16],
        )


@dataclass
class Validity:
    """Every regulatory claim is time-bounded. 'What applied on date X' must be a query."""
    start: Optional[str] = None   # ISO date
    end: Optional[str] = None

    def applies_on(self, d: date) -> bool:
        if self.start and d < date.fromisoformat(self.start):
            return False
        if self.end and d > date.fromisoformat(self.end):
            return False
        return True


@dataclass
class Gap:
    """Something a source says that the ontology cannot express."""
    kind: str
    subject: str
    detail: str
    provenance: Provenance
    suggested: dict = field(default_factory=dict)

    def key(self) -> str:
        return f"{self.kind}:{self.subject}:{self.detail}"[:200]


@dataclass
class Delta:
    """A proposed change to the ontology. Never applied without passing the gate."""
    kind: DeltaKind
    target: str
    body: dict
    provenance: Provenance
    confidence: Confidence
    rationale: str
    validity: Optional[Validity] = None

    def auto_mergeable(self) -> bool:
        """Tier 1 product-catalogue churn merges itself. Anything touching an
        obligation, a licence, or an unstructured extraction goes to a human."""
        if self.provenance.tier != Tier.AUTHORITATIVE_STRUCTURED:
            return False
        if self.kind in (DeltaKind.RETIRE, DeltaKind.SET_VALIDITY):
            return False
        if self.touches_obligation():
            return False
        return True

    def touches_obligation(self) -> bool:
        blob = json.dumps(self.body).lower()
        return any(t in blob for t in (
            "regulatoryreference", "obligation", "licence", "license",
            "prudential", "accountab", "breach", "designatedservice"))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["kind"] = self.kind.value
        d["confidence"] = self.confidence.value
        d["provenance"]["tier"] = int(self.provenance.tier)
        return d
