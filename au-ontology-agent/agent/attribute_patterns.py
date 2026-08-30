"""Pattern generator for products without a curated spec.

Three detail levels, and the distinction is the point:
  curated   - hand-specified against Australian sources
  patterned - generated from group + keyword rules, plausible but unverified
  stub      - key and label only

Patterned products get realistic column sets so the model is joinable and
demonstrable, but they carry confidence "notVerified" and must not be presented
as designed. Prompts 19-23 replace them.
"""
from __future__ import annotations

A = lambda n, t, req, cdr, reg, cls, src: (n, t, "N" if req else "Y", cdr, reg, cls, src)

# ---------- packs every product gets ----------
def identity(pid: str) -> list:
    return [
        A(f"{pid}_id", "STRING", 1, None, None, "reference", "core banking"),
        A("business_key", "STRING", 0, None, None, "reference", "core banking"),
        A("label", "STRING", 1, None, None, "reference", "core banking"),
        A("status", "STRING", 1, None, None, "reference", "core banking"),
        A("status_reason", "STRING", 0, None, None, "reference", "core banking"),
    ]

LIFECYCLE = [
    A("effective_from", "DATE", 1, None, "point-in-time reporting", "regulatory", "core banking"),
    A("effective_to", "DATE", 0, None, "point-in-time reporting", "regulatory", "core banking"),
    A("is_current_ind", "BOOLEAN", 1, None, None, "derived", "ingestion"),
]

AUDIT = [
    A("created_ts", "TIMESTAMP", 1, None, None, "reference", "core banking"),
    A("created_by", "STRING", 1, None, None, "reference", "core banking"),
    A("updated_ts", "TIMESTAMP", 1, None, None, "reference", "core banking"),
    A("updated_by", "STRING", 1, None, None, "reference", "core banking"),
    A("source_system", "STRING", 1, None, "CPG 235 lineage", "regulatory", "ingestion"),
    A("source_record_id", "STRING", 0, None, "CPG 235 lineage", "regulatory", "ingestion"),
    A("ingested_ts", "TIMESTAMP", 1, None, None, "reference", "ingestion"),
    A("record_hash", "STRING", 0, None, None, "derived", "ingestion"),
    A("dq_score", "DECIMAL(5,2)", 0, None, "CPG 235 data quality", "derived", "data quality"),
]

# ---------- packs by group ----------
GROUP = {
"party": [
    A("party_type", "STRING", 1, None, "ARS 701.0 counterparty sector", "regulatory", "core banking"),
    A("legal_name", "STRING", 1, None, None, "pii", "core banking"),
    A("trading_name", "STRING", 0, None, None, "reference", "core banking"),
    A("country_of_domicile", "STRING", 1, None, "ARS 701.0 residency", "regulatory", "core banking"),
    A("primary_address_id", "STRING", 0, None, None, "pii", "address validation"),
    A("kyc_status", "STRING", 1, None, "AML/CTF CDD", "regulatory", "KYC platform"),
    A("kyc_last_reviewed", "DATE", 0, None, "AML/CTF", "regulatory", "KYC platform"),
    A("risk_rating", "STRING", 1, None, "AML/CTF customer risk", "sensitive", "AML engine"),
    A("sanctions_screened_ts", "TIMESTAMP", 0, None, "DFAT sanctions", "sensitive", "screening"),
    A("consent_marketing_ind", "BOOLEAN", 1, None, "Privacy Act APP 7", "sensitive", "CRM"),
],
"role": [
    A("party_id", "STRING", 1, None, None, "pii", "CRM"),
    A("role_type", "STRING", 1, None, None, "reference", "CRM"),
    A("brand_id", "STRING", 0, None, None, "reference", "CRM"),
    A("appointed_date", "DATE", 1, None, None, "reference", "CRM"),
    A("ceased_date", "DATE", 0, None, None, "reference", "CRM"),
    A("authority_basis", "STRING", 0, None, None, "regulatory", "core banking"),
    A("evidence_sighted_ind", "BOOLEAN", 1, None, "AML/CTF CDD", "regulatory", "KYC platform"),
    A("delegated_limit_amount", "DECIMAL(18,2)", 0, None, None, "financial", "entitlements"),
],
"dep": [
    A("party_id", "STRING", 1, None, None, "pii", "core banking"),
    A("brand_id", "STRING", 1, None, None, "reference", "core banking"),
    A("product_id", "STRING", 1, "account.productCategory", None, "reference", "product catalogue"),
    A("bsb", "STRING", 0, None, "AusPayNet BSB", "reference", "core banking"),
    A("currency", "STRING", 1, "balance.currency", "ARS 701.0 currency", "regulatory", "core banking"),
    A("current_balance", "DECIMAL(18,2)", 1, "balance.currentBalance", None, "financial", "core banking"),
    A("available_balance", "DECIMAL(18,2)", 1, "balance.availableBalance", None, "financial", "core banking"),
    A("interest_rate_pct", "DECIMAL(6,4)", 0, "depositRate.rate", "ARF 747 rate", "financial", "core banking"),
    A("depositor_sector", "STRING", 1, None, "ARF 747 household/business/community", "regulatory", "core banking"),
    A("fcs_covered_ind", "BOOLEAN", 1, None, "Banking Act FCS", "regulatory", "internal"),
    A("opened_date", "DATE", 1, None, None, "reference", "core banking"),
    A("closed_date", "DATE", 0, None, None, "reference", "core banking"),
    A("dormant_ind", "BOOLEAN", 1, None, "ASIC unclaimed money", "regulatory", "core banking"),
],
"credit": [
    A("borrower_party_id", "STRING", 1, None, None, "pii", "lending"),
    A("brand_id", "STRING", 1, None, None, "reference", "lending"),
    A("product_id", "STRING", 1, None, None, "reference", "product catalogue"),
    A("limit_amount", "DECIMAL(18,2)", 1, None, "APS 112 undrawn exposure", "financial", "lending"),
    A("outstanding_balance", "DECIMAL(18,2)", 1, "balance.amount", None, "financial", "lending"),
    A("interest_rate_pct", "DECIMAL(6,4)", 0, "lendingRate.rate", None, "financial", "lending"),
    A("interest_rate_type", "STRING", 1, "lendingRate.lendingRateType", "ARS 701.0 rate type", "regulatory", "lending"),
    A("loan_purpose", "STRING", 1, None, "ARS 701.0 loan purpose", "regulatory", "lending"),
    A("borrower_type", "STRING", 1, None, "ARS 701.0 borrower type", "regulatory", "lending"),
    A("anzsic_code", "STRING", 0, None, "ARS 701.0 ANZSIC 2006", "regulatory", "credit risk"),
    A("security_type", "STRING", 0, None, "ARS 701.0 security type", "regulatory", "collateral"),
    A("origination_channel", "STRING", 1, None, None, "reference", "lending"),
    A("originating_broker_id", "STRING", 0, None, "NCCP best interests duty", "regulatory", "broker portal"),
    A("arrears_days", "INT", 1, None, "ARF 744 arrears bucket", "financial", "collections"),
    A("provision_amount", "DECIMAL(18,2)", 0, None, "APS 220 provisioning", "financial", "credit risk"),
    A("risk_weight_pct", "DECIMAL(5,2)", 0, None, "APS 112 / APS 113", "regulatory", "capital"),
    A("settled_date", "DATE", 0, None, None, "financial", "lending"),
    A("maturity_date", "DATE", 0, None, None, "financial", "lending"),
],
"mkt": [
    A("counterparty_party_id", "STRING", 1, None, None, "reference", "treasury"),
    A("notional_amount", "DECIMAL(18,2)", 0, None, "ARF 722 derivatives", "financial", "treasury"),
    A("currency", "STRING", 1, None, None, "regulatory", "treasury"),
    A("trade_date", "DATE", 0, None, None, "financial", "treasury"),
    A("maturity_date", "DATE", 0, None, None, "financial", "treasury"),
    A("mark_to_market_amount", "DECIMAL(18,2)", 0, None, "APS 112 exposure", "financial", "treasury"),
    A("collateral_posted_amount", "DECIMAL(18,2)", 0, None, "CPS 226 margining", "regulatory", "treasury"),
    A("booking_entity", "STRING", 1, None, "APS 222 related entities", "regulatory", "treasury"),
    A("afsl_authorisation", "STRING", 0, None, "ASIC AFSL", "regulatory", "compliance"),
    A("client_classification", "STRING", 1, None, "retail vs wholesale client", "regulatory", "compliance"),
],
"ins": [
    A("policy_number", "STRING", 1, None, None, "reference", "insurance"),
    A("insured_party_id", "STRING", 1, None, None, "pii", "insurance"),
    A("underwriter_party_id", "STRING", 1, None, "APRA GPS/LPS regulated", "regulatory", "insurance"),
    A("distributor_party_id", "STRING", 1, None, "ASIC AFSL", "regulatory", "insurance"),
    A("sum_insured", "DECIMAL(18,2)", 0, None, None, "financial", "insurance"),
    A("premium_amount", "DECIMAL(18,2)", 0, None, None, "financial", "insurance"),
    A("premium_frequency", "STRING", 0, None, None, "reference", "insurance"),
    A("inception_date", "DATE", 1, None, None, "financial", "insurance"),
    A("expiry_date", "DATE", 0, None, None, "financial", "insurance"),
    A("tmd_id", "STRING", 0, None, "ASIC RG 274", "regulatory", "product governance"),
    A("deferred_sales_applied_ind", "BOOLEAN", 0, None, "ASIC RG 275", "regulatory", "insurance"),
    A("code_subscriber_ind", "BOOLEAN", 1, None, "General or Life Insurance Code", "regulatory", "compliance"),
],
"prod": [
    A("brand_id", "STRING", 1, "product.brand", None, "reference", "product catalogue"),
    A("product_category", "STRING", 1, "product.productCategory", None, "reference", "product catalogue"),
    A("product_name", "STRING", 1, "product.name", None, "reference", "product catalogue"),
    A("description", "STRING", 0, "product.description", None, "reference", "product catalogue"),
    A("effective_from_dt", "TIMESTAMP", 1, "product.effectiveFrom", None, "reference", "product catalogue"),
    A("effective_to_dt", "TIMESTAMP", 0, "product.effectiveTo", None, "reference", "product catalogue"),
    A("cdr_scope_status", "STRING", 1, None, "CDR mandatory/voluntary/out", "regulatory", "internal"),
    A("tmd_id", "STRING", 0, None, "ASIC RG 274", "regulatory", "product governance"),
    A("target_market_summary", "STRING", 0, None, "ASIC RG 274", "regulatory", "product governance"),
    A("owner_employee_id", "STRING", 1, None, "product owner accountability", "regulatory", "product governance"),
    A("withdrawn_ind", "BOOLEAN", 1, None, None, "reference", "product catalogue"),
],
"event": [
    A("event_ts", "TIMESTAMP", 1, "transaction.postingDateTime", None, "financial", "event stream"),
    A("value_date", "DATE", 0, "transaction.valueDateTime", None, "financial", "event stream"),
    A("party_id", "STRING", 0, None, None, "pii", "event stream"),
    A("account_id", "STRING", 0, "transaction.accountId", None, "reference", "core banking"),
    A("channel_id", "STRING", 0, None, None, "reference", "channel ops"),
    A("amount", "DECIMAL(18,2)", 0, "transaction.amount", None, "financial", "event stream"),
    A("currency", "STRING", 0, "transaction.currency", None, "regulatory", "event stream"),
    A("initiated_by", "STRING", 1, None, None, "reference", "event stream"),
    A("outcome", "STRING", 1, None, None, "reference", "event stream"),
    A("reason_code", "STRING", 0, None, None, "reference", "event stream"),
    A("reference_number", "STRING", 0, None, None, "reference", "event stream"),
    A("reportable_ind", "BOOLEAN", 1, None, "triggers a regulatory report", "regulatory", "compliance"),
],
"asset": [
    A("owner_party_id", "STRING", 0, None, None, "pii", "collateral"),
    A("asset_type", "STRING", 1, None, "ARS 701.0 security type", "regulatory", "collateral"),
    A("description", "STRING", 0, None, None, "reference", "collateral"),
    A("valuation_amount", "DECIMAL(18,2)", 0, None, "APS 112 collateral value", "financial", "valuation"),
    A("valuation_date", "DATE", 0, None, None, "financial", "valuation"),
    A("valuation_basis", "STRING", 0, None, "APS 112", "regulatory", "valuation"),
    A("jurisdiction", "STRING", 0, None, None, "reference", "collateral"),
    A("registration_number", "STRING", 0, None, "PPSR or titles registry", "regulatory", "registry"),
    A("encumbrance_ind", "BOOLEAN", 1, None, None, "financial", "collateral"),
],
"place": [
    A("name", "STRING", 1, None, None, "reference", "reference data"),
    A("location_type", "STRING", 1, None, None, "reference", "reference data"),
    A("address_id", "STRING", 0, None, None, "pii", "address validation"),
    A("jurisdiction", "STRING", 0, None, None, "reference", "reference data"),
    A("operating_hours", "STRING", 0, None, None, "reference", "channel ops"),
    A("accessibility_features", "STRING", 0, None, "ABA Code B1 inclusive banking", "regulatory", "channel ops"),
    A("opened_date", "DATE", 0, None, None, "reference", "channel ops"),
    A("closed_date", "DATE", 0, None, None, "regulatory", "channel ops"),
],
"reg": [
    A("instrument", "STRING", 1, None, "the standard or rule this satisfies", "regulatory", "GRC"),
    A("regulator", "STRING", 1, None, None, "regulatory", "GRC"),
    A("obligation_reference", "STRING", 1, None, None, "regulatory", "GRC"),
    A("reporting_period", "DATE", 0, None, None, "regulatory", "reg reporting"),
    A("due_date", "DATE", 0, None, None, "regulatory", "reg reporting"),
    A("submitted_ts", "TIMESTAMP", 0, None, None, "regulatory", "reg reporting"),
    A("submitted_by_employee_id", "STRING", 0, None, "FAR accountability", "regulatory", "GRC"),
    A("accountable_person_id", "STRING", 0, None, "FAR", "regulatory", "GRC"),
    A("breach_ind", "BOOLEAN", 1, None, "ASIC reportable situation", "regulatory", "GRC"),
    A("evidence_uri", "STRING", 0, None, "audit evidence", "regulatory", "GRC"),
],
"scheme": [
    A("scheme_name", "STRING", 1, None, None, "reference", "payments"),
    A("operator_party_id", "STRING", 1, None, None, "reference", "payments"),
    A("scheme_model", "STRING", 1, None, "three-party or four-party", "regulatory", "payments"),
    A("rba_designated_ind", "BOOLEAN", 1, None, "RBA designation", "regulatory", "payments"),
    A("rules_version", "STRING", 0, None, None, "reference", "payments"),
    A("participation_status", "STRING", 1, None, None, "reference", "payments"),
    A("settlement_window", "STRING", 0, None, None, "reference", "payments"),
],
"prov": [
    A("provider_name", "STRING", 1, None, None, "reference", "procurement"),
    A("abn", "STRING", 0, None, None, "reference", "ABN Lookup"),
    A("service_category", "STRING", 1, None, None, "reference", "procurement"),
    A("material_service_provider_ind", "BOOLEAN", 1, None, "CPS 230 MSP register", "regulatory", "GRC"),
    A("contract_id", "STRING", 0, None, None, "reference", "procurement"),
    A("contract_expiry", "DATE", 0, None, "CPS 230 transition", "regulatory", "procurement"),
    A("regulator_of_provider", "STRING", 0, None, None, "regulatory", "GRC"),
    A("assurance_report_type", "STRING", 0, None, "ASAE 3150 / ISO 27001", "regulatory", "GRC"),
],
"body": [
    A("body_name", "STRING", 1, None, None, "reference", "GRC"),
    A("body_type", "STRING", 1, None, "regulator, government, industry body", "regulatory", "GRC"),
    A("instruments_administered", "STRING", 1, None, None, "regulatory", "GRC"),
    A("reporting_channel", "STRING", 0, None, None, "regulatory", "reg reporting"),
    A("notification_window_hours", "INT", 0, None, "incident notification", "regulatory", "GRC"),
    A("relationship_owner_employee_id", "STRING", 0, None, None, "reference", "GRC"),
],
"loy": [
    A("program_id", "STRING", 1, None, None, "reference", "loyalty"),
    A("points_currency", "STRING", 0, None, None, "reference", "loyalty"),
    A("points_amount", "BIGINT", 0, None, None, "financial", "loyalty"),
    A("monetary_value", "DECIMAL(18,4)", 0, None, "AASB 15 measurement", "financial", "finance"),
    A("member_party_id", "STRING", 0, None, None, "pii", "loyalty"),
    A("earn_or_burn", "STRING", 0, None, None, "reference", "loyalty"),
    A("terms_version", "STRING", 0, None, "ACCC loyalty review", "regulatory", "loyalty"),
    A("expiry_date", "DATE", 0, None, "ACCC expiry disclosure", "regulatory", "loyalty"),
],
}

# ---------- keyword enrichment ----------
KEYWORD = [
 (("card",), [
   A("scheme_id","STRING",1,None,"RBA designated scheme","regulatory","cards"),
   A("card_number_token","STRING",0,None,"PCI DSS - tokenised","pii","cards"),
   A("expiry_month_year","STRING",0,None,None,"pii","cards"),
   A("interchange_category","STRING",0,None,"RBA Standard No.1","regulatory","cards"),
   A("dual_network_ind","BOOLEAN",0,None,"least-cost routing eligible","regulatory","cards")]),
 (("payment","transfer","settle","payto","payid","osko","bpay"), [
   A("payment_rail","STRING",1,None,"NPP / BECS / RTGS","regulatory","payments hub"),
   A("payer_account_id","STRING",0,None,None,"financial","payments hub"),
   A("payee_identifier","STRING",0,None,"BSB+account or PayID","pii","payments hub"),
   A("cross_border_ind","BOOLEAN",1,None,"AUSTRAC IFTI","regulatory","payments hub"),
   A("iso20022_message_type","STRING",0,None,"ISO 20022","regulatory","payments hub")]),
 (("loan","facility","mortgage","credit","lend","overdraft","finance"), [
   A("lvr_pct","DECIMAL(5,2)",0,None,"APS 112 LVR","financial","credit risk"),
   A("serviceability_buffer_pct","DECIMAL(5,2)",0,None,"APRA serviceability buffer","regulatory","credit decisioning"),
   A("responsible_lending_assessed_ind","BOOLEAN",0,None,"NCCP responsible lending","regulatory","credit decisioning"),
   A("hardship_ind","BOOLEAN",0,None,"CR Code financial hardship","sensitive","hardship")]),
 (("insur","policy","claim","lmi"), [
   A("claim_count","INT",0,None,None,"financial","insurance"),
   A("claims_handling_afsl","STRING",0,None,"licensed since 1 Jan 2022","regulatory","claims")]),
 (("alert","screen","aml","sanction","fraud","scam","pep"), [
   A("detection_rule_id","STRING",0,None,None,"sensitive","AML engine"),
   A("investigator_employee_id","STRING",0,None,None,"sensitive","case management"),
   A("escalated_ind","BOOLEAN",1,None,None,"sensitive","case management"),
   A("regulator_report_id","STRING",0,None,"SMR / TTR / IFTI","regulatory","AML engine"),
   A("tipping_off_restricted_ind","BOOLEAN",1,None,"AML/CTF Act s123","sensitive","AML engine")]),
 (("complaint","dispute","determination","remediation"), [
   A("received_date","DATE",1,None,"RG 271 timeframes","regulatory","complaints"),
   A("resolution_date","DATE",0,None,"RG 271 30 days","regulatory","complaints"),
   A("product_code","STRING",0,None,"RG 271 IDR schema","regulatory","complaints"),
   A("issue_code","STRING",0,None,"RG 271 IDR schema","regulatory","complaints"),
   A("compensation_amount","DECIMAL(18,2)",0,None,None,"financial","complaints")]),
 (("broker","aggregator","distributor","referrer","adviser","introducer"), [
   A("acl_or_afsl_number","STRING",0,None,"ASIC licence","regulatory","ASIC register"),
   A("commission_amount","DECIMAL(18,2)",0,None,None,"financial","finance"),
   A("accreditation_expiry","DATE",0,None,None,"regulatory","broker portal")]),
 (("trust","smsf","estate","attorney","executor","guarantor","signatory"), [
   A("authority_document_type","STRING",0,None,"deed, probate, POA","regulatory","core banking"),
   A("authority_verified_ts","TIMESTAMP",0,None,"AML/CTF CDD","regulatory","KYC platform"),
   A("acting_for_party_id","STRING",0,None,None,"pii","core banking")]),
 (("branch","atm","channel","post","terminal","digital"), [
   A("availability_pct","DECIMAL(5,2)",0,None,"CPS 230 tolerance","regulatory","channel ops"),
   A("operated_by_party_id","STRING",0,None,"often a third party","regulatory","channel ops"),
   A("transaction_volume_monthly","BIGINT",0,None,None,"financial","channel ops")]),
 (("consent","cdr"), [
   A("consent_scope","STRING",0,None,"CDR Rules","regulatory","CDR gateway"),
   A("data_recipient_id","STRING",0,None,"CDR accreditation number","regulatory","CDR Register"),
   A("expiry_ts","TIMESTAMP",0,"sharingExpiresAt","CDR Rules","regulatory","CDR gateway"),
   A("revoked_ts","TIMESTAMP",0,None,"CDR Rules","regulatory","CDR gateway")]),
 (("guarantee","scheme guarantee","housing"), [
   A("guarantor_party_id","STRING",0,None,None,"pii","lending"),
   A("guaranteed_amount","DECIMAL(18,2)",0,None,None,"financial","lending"),
   A("guarantee_pct","DECIMAL(5,2)",0,None,None,"financial","lending")]),
]


def patterned(pid: str, label: str, group: str, fk_targets: list[tuple[str, str]]) -> list:
    """Assemble a plausible column set: identity, group pack, keyword packs,
    FK columns, lifecycle, audit. Deduplicated, key first."""
    cols, seen = [], set()

    def add(rows):
        for r in rows:
            if r[0] not in seen:
                seen.add(r[0]); cols.append(r)

    add(identity(pid))
    add(GROUP.get(group, []))
    low = label.lower()
    for keys, pack in KEYWORD:
        if any(k in low for k in keys):
            add(pack)
    # foreign key columns make the model joinable
    for target_pid, target_pk in fk_targets[:8]:
        add([A(target_pk if target_pk not in seen else f"{target_pid}_ref",
               "STRING", 0, None, None, "reference", "core banking")])
    add(LIFECYCLE)
    add(AUDIT)
    return cols
