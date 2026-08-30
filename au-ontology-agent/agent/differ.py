"""Maps an authoritative payload onto the ontology and emits structured gaps.

The differ never writes. It answers one question: what does this source say
that the model cannot currently express?
"""
from __future__ import annotations
import json, re
from pathlib import Path
from agent.model import Gap, Provenance, Tier

# CDR banking product categories -> ontology class ids.
# Anything not in this map is, by definition, a gap.
CDR_CATEGORY_MAP = {
    "TRANS_AND_SAVINGS_ACCOUNTS": "account",
    "TERM_DEPOSITS":              "termDeposit",
    "RESIDENTIAL_MORTGAGES":      "facility",
    "CRED_AND_CHRG_CARDS":        "cardAccount",
    "PERS_LOANS":                 "personalLoan",
    "MARGIN_LOANS":               "marginLoan",
    "LEASES":                     "novated",
    "TRADE_FINANCE":              "lc",
    "OVERDRAFTS":                 "overdraft",
    "BUSINESS_LOANS":             "facility",
    "REGULATED_TRUST_ACCOUNTS":   "statutoryTrust",
    "TRAVEL_CARDS":               "travelCard",
}

# CDR feature types we already model
CDR_FEATURE_MAP = {
    "OFFSET": "offset", "REDRAW": "feature", "CARD_ACCESS": "card",
    "ADDITIONAL_CARDS": "addlCardholder", "INSURANCE": "insurancePolicy",
    "LOYALTY_PROGRAM": "loyaltyProgram", "BONUS_REWARDS": "bonusOffer",
    "DIGITAL_WALLET": "wallet", "NPP_PAYID": "payid", "NPP_ENABLED": "osko",
    "BILL_PAYMENT": "bpay", "OVERDRAFT": "overdraft",
    "INTEREST_FREE": "noInterestCard", "INSTALMENT_PLAN": "instalment",
    "GUARANTOR": "guarantor", "NOTIFICATIONS": "interaction",
    "FREE_TXNS": "feeSchedule", "CASHBACK_OFFER": "merchantOffer",
}


class Differ:
    def __init__(self, model_path: str):
        self.model = json.loads(Path(model_path).read_text())
        self.class_ids = {c["id"] for c in self.model["classes"]}
        self.labels = {c["label"].lower() for c in self.model["classes"]}

    # ---------- CDR product reference data ----------
    def diff_cdr_products(self, brand: str, payload: dict, url: str) -> list[Gap]:
        prov = Provenance.of("cdr_products", Tier.AUTHORITATIVE_STRUCTURED, url, payload)
        gaps: list[Gap] = []
        products = payload.get("data", {}).get("products", [])
        for p in products:
            cat = p.get("productCategory")
            if cat and cat not in CDR_CATEGORY_MAP:
                gaps.append(Gap("unmappedProductCategory", cat,
                                f'{brand}: category not in the model', prov,
                                {"kind": "addClass", "group": "credit",
                                 "label": self._humanise(cat)}))
            elif cat and CDR_CATEGORY_MAP[cat] not in self.class_ids:
                gaps.append(Gap("mappedClassMissing", CDR_CATEGORY_MAP[cat],
                                f'{brand}: mapping target absent from model', prov))
            for f in p.get("features", []) or []:
                ft = f.get("featureType")
                if ft and ft not in CDR_FEATURE_MAP:
                    gaps.append(Gap("unmappedFeature", ft,
                                    f'{brand}: product feature not modelled', prov,
                                    {"kind": "addClass", "group": "prod",
                                     "label": self._humanise(ft)}))
            if p.get("bundles") and "package" not in self.class_ids:
                gaps.append(Gap("unmappedStructure", "bundle",
                                f'{brand}: product bundling not modelled', prov))
        return self._dedupe(gaps)

    # ---------- CDR data holder brands ----------
    def diff_cdr_brands(self, payload: dict, url: str) -> list[Gap]:
        prov = Provenance.of("cdr_register", Tier.AUTHORITATIVE_STRUCTURED, url, payload)
        gaps = []
        for b in payload.get("data", []):
            name = b.get("brandName", "")
            if name and name.lower() not in self.labels:
                gaps.append(Gap("unknownBrand", name,
                                "registered CDR data holder brand absent from model", prov,
                                {"kind": "addClass", "group": "party", "label": name}))
        return self._dedupe(gaps)

    # ---------- legislation / standards ----------
    def diff_legislation(self, items: list[dict], url: str) -> list[Gap]:
        """Tier 1 detection only. A commencement date is a validity interval,
        and validity changes never auto-merge."""
        prov = Provenance.of("legislation_register", Tier.AUTHORITATIVE_STRUCTURED, url, items)
        gaps = []
        for it in items:
            title = it.get("title", "")
            if re.search(r"bank|credit|insur|payment|financ|privacy|money laundering",
                         title, re.I):
                gaps.append(Gap("regulatoryChange", title[:120],
                                it.get("summary", "")[:200], prov,
                                {"kind": "setValidity", "commences": it.get("commences")}))
        return self._dedupe(gaps)

    @staticmethod
    def _humanise(code: str) -> str:
        return " ".join(w.capitalize() for w in code.replace("_", " ").split())

    @staticmethod
    def _dedupe(gaps: list[Gap]) -> list[Gap]:
        seen, out = set(), []
        for g in gaps:
            if g.key() not in seen:
                seen.add(g.key()); out.append(g)
        return out
