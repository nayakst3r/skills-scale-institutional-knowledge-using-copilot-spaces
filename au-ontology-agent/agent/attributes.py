"""Attribute layer, in the Databricks industry-data-model shape.

Their hierarchy:  Domain -> Sub-domain -> Product (table) -> Attribute (column)
Ours maps:        Group  -> Class                          -> Attribute

Every attribute carries the Australian bindings that make the model usable:
  cdr        CDR banking payload field, where one exists
  efs        APRA EFS / ARF reporting dimension it feeds
  cls        classification: pii | sensitive | regulatory | financial | reference | derived
  src        typical source system
"""
from __future__ import annotations

# ---- reusable column packs -------------------------------------------------
AUDIT = [
    ("created_ts", "TIMESTAMP", "N", None, None, "reference", "core banking"),
    ("updated_ts", "TIMESTAMP", "N", None, None, "reference", "core banking"),
    ("source_system", "STRING", "N", None, None, "reference", "ingestion"),
    ("record_hash", "STRING", "Y", None, None, "derived", "ingestion"),
]
VALIDITY = [
    ("valid_from", "DATE", "N", None, None, "regulatory", "core banking"),
    ("valid_to", "DATE", "Y", None, None, "regulatory", "core banking"),
]

# ---- curated Australian attribute specs -----------------------------------
# class_id: (pk, [(name, type, nullable, cdr_field, efs_dimension, classification, source)])
SPEC: dict[str, tuple[str, list]] = {

"person": ("party_id", [
    ("party_id","STRING","N","customer.personId",None,"pii","core banking"),
    ("given_name","STRING","N","person.firstName",None,"pii","core banking"),
    ("family_name","STRING","N","person.lastName",None,"pii","core banking"),
    ("date_of_birth","DATE","N",None,None,"pii","core banking"),
    ("tfn_supplied_ind","BOOLEAN","N",None,"ATO TFN withholding","regulatory","core banking"),
    ("residency_status","STRING","N",None,"ARS 701.0 resident/non-resident","regulatory","core banking"),
    ("foreign_tax_resident_ind","BOOLEAN","N",None,"FATCA/CRS","regulatory","KYC platform"),
    ("pep_flag","BOOLEAN","N",None,"AML/CTF Rules","sensitive","AML engine"),
    ("sanctions_match_ind","BOOLEAN","N",None,"DFAT sanctions","sensitive","screening"),
    ("vulnerability_flag","BOOLEAN","N",None,"ABA Code B2","sensitive","CRM"),
    ("deceased_ind","BOOLEAN","N",None,"ABA Code B8","sensitive","core banking"),
]),

"org": ("party_id", [
    ("party_id","STRING","N","customer.organisationId",None,"reference","core banking"),
    ("legal_name","STRING","N","organisation.businessName",None,"reference","core banking"),
    ("abn","STRING","Y","organisation.abn",None,"reference","ABN Lookup"),
    ("acn","STRING","Y","organisation.acn",None,"reference","ASIC register"),
    ("lei","STRING","Y",None,"ISO 17442","reference","GLEIF"),
    ("anzsic_code","STRING","N",None,"ARS 701.0 ANZSIC 2006","regulatory","credit risk"),
    ("entity_type","STRING","N","organisation.organisationType",None,"reference","core banking"),
    ("registered_country","STRING","N","organisation.registeredCountry",None,"regulatory","ABN Lookup"),
    ("beneficial_owner_verified_ind","BOOLEAN","N",None,"AML/CTF tranche 2","sensitive","KYC platform"),
]),

"adi": ("adi_id", [
    ("adi_id","STRING","N",None,None,"reference","APRA register"),
    ("legal_name","STRING","N",None,None,"reference","APRA register"),
    ("abn","STRING","N",None,None,"reference","ABN Lookup"),
    ("adi_type","STRING","N",None,"APRA ADI category","regulatory","APRA register"),
    ("foreign_owned_ind","BOOLEAN","N",None,None,"regulatory","APRA register"),
    ("fcs_group_id","STRING","N",None,"Banking Act FCS","regulatory","internal"),
]),

"brand": ("brand_id", [
    ("brand_id","STRING","N","dataHolderBrandId",None,"reference","CDR Register"),
    ("brand_name","STRING","N","brandName",None,"reference","CDR Register"),
    ("adi_id","STRING","N",None,None,"reference","internal"),
    ("cdr_registered_ind","BOOLEAN","N",None,"CDR Rules","regulatory","CDR Register"),
    ("public_base_uri","STRING","Y","publicBaseUri",None,"reference","CDR Register"),
    ("core_system_id","STRING","Y",None,None,"reference","internal"),
]),

"facility": ("facility_id", [
    ("facility_id","STRING","N","account.accountId",None,"financial","lending"),
    ("brand_id","STRING","N",None,None,"reference","internal"),
    ("product_id","STRING","N","account.productCategory",None,"reference","product catalogue"),
    ("borrower_party_id","STRING","N",None,None,"pii","lending"),
    ("limit_amount","DECIMAL(18,2)","N","loan.maxRedraw",None,"financial","lending"),
    ("drawn_balance","DECIMAL(18,2)","N","balance.amount",None,"financial","lending"),
    ("loan_purpose","STRING","N",None,"ARS 701.0 loan purpose","regulatory","lending"),
    ("borrower_type","STRING","N",None,"ARS 701.0 borrower type","regulatory","lending"),
    ("occupancy_type","STRING","N",None,"ARF 743/744 owner-occ vs investor","regulatory","lending"),
    ("repayment_type","STRING","N","lendingRate.repaymentType","ARF 744 P&I vs IO","regulatory","lending"),
    ("interest_rate_type","STRING","N","lendingRate.lendingRateType","ARS 701.0 rate type","regulatory","lending"),
    ("security_type","STRING","Y",None,"ARS 701.0 security type","regulatory","collateral"),
    ("lvr_pct","DECIMAL(5,2)","Y",None,"APS 112 risk weight input","financial","credit risk"),
    ("arrears_days","INT","N",None,"ARF 744 arrears bucket","financial","collections"),
    ("hardship_ind","BOOLEAN","N",None,"CR Code FHI","sensitive","hardship"),
    ("securitised_ind","BOOLEAN","N",None,"APS 120","regulatory","treasury"),
] + VALIDITY),

"account": ("account_id", [
    ("account_id","STRING","N","account.accountId",None,"financial","core banking"),
    ("brand_id","STRING","N",None,None,"reference","internal"),
    ("bsb","STRING","N",None,"AusPayNet BSB","reference","core banking"),
    ("account_number","STRING","N","account.accountNumber",None,"pii","core banking"),
    ("display_name","STRING","N","account.displayName",None,"pii","core banking"),
    ("product_category","STRING","N","account.productCategory",None,"reference","product catalogue"),
    ("current_balance","DECIMAL(18,2)","N","balance.currentBalance",None,"financial","core banking"),
    ("available_balance","DECIMAL(18,2)","N","balance.availableBalance",None,"financial","core banking"),
    ("currency","STRING","N","balance.currency",None,"regulatory","core banking"),
    ("depositor_type","STRING","N",None,"ARF 747 household/business","regulatory","core banking"),
    ("fcs_covered_ind","BOOLEAN","N",None,"Banking Act FCS $250k per ADI","regulatory","internal"),
    ("dormant_ind","BOOLEAN","N",None,"ASIC unclaimed money","regulatory","core banking"),
    ("joint_ind","BOOLEAN","N",None,"ABA Code C1","reference","core banking"),
] + VALIDITY),

"offset": ("offset_account_id", [
    ("offset_account_id","STRING","N","account.accountId",None,"financial","core banking"),
    ("linked_facility_id","STRING","N",None,None,"financial","lending"),
    ("linked_split_id","STRING","Y",None,None,"financial","lending"),
    ("offset_type","STRING","N",None,None,"reference","product catalogue"),
    ("offset_balance","DECIMAL(18,2)","N","balance.currentBalance",None,"financial","core banking"),
    ("efs_reported_gross_ind","BOOLEAN","N",None,"ARS 701.0 gross of offset","regulatory","reg reporting"),
]),

"cardAccount": ("card_account_id", [
    ("card_account_id","STRING","N","account.accountId",None,"financial","cards"),
    ("scheme","STRING","N",None,"RBA card scheme","reference","cards"),
    ("scheme_model","STRING","N",None,"three-party vs four-party","reference","cards"),
    ("credit_limit","DECIMAL(18,2)","N","creditCard.minPaymentAmount",None,"financial","cards"),
    ("interchange_category","STRING","N",None,"RBA Standard No.1","regulatory","cards"),
    ("rewards_program_id","STRING","Y",None,None,"reference","loyalty"),
    ("is_white_label_ind","BOOLEAN","N",None,None,"reference","cards"),
    ("issuer_adi_id","STRING","N",None,None,"reference","cards"),
]),

"pointsBalance": ("points_balance_id", [
    ("points_balance_id","STRING","N",None,None,"financial","loyalty"),
    ("card_account_id","STRING","N",None,None,"reference","loyalty"),
    ("points_currency","STRING","N",None,None,"reference","loyalty"),
    ("balance_points","BIGINT","N",None,None,"financial","loyalty"),
    ("expiry_rule","STRING","N",None,"ACCC loyalty review","regulatory","loyalty"),
    ("next_expiry_date","DATE","Y",None,None,"financial","loyalty"),
    ("liability_amount","DECIMAL(18,2)","N",None,"AASB 15 contract liability","financial","finance"),
    ("breakage_pct","DECIMAL(5,2)","N",None,"AASB 15 breakage","derived","finance"),
]),

"payment": ("payment_id", [
    ("payment_id","STRING","N","transaction.transactionId",None,"financial","payments hub"),
    ("account_id","STRING","N","transaction.accountId",None,"financial","payments hub"),
    ("amount","DECIMAL(18,2)","N","transaction.amount",None,"financial","payments hub"),
    ("currency","STRING","N","transaction.currency",None,"regulatory","payments hub"),
    ("rail","STRING","N",None,"NPP / BECS / RTGS","reference","payments hub"),
    ("payid","STRING","Y",None,"NPP addressing","pii","payments hub"),
    ("payee_name","STRING","Y","transaction.description",None,"pii","payments hub"),
    ("cop_result","STRING","Y",None,"Confirmation of Payee","sensitive","payments hub"),
    ("cross_border_ind","BOOLEAN","N",None,"AUSTRAC IFTI","regulatory","payments hub"),
    ("cash_amount","DECIMAL(18,2)","Y",None,"AUSTRAC TTR $10k","regulatory","branch"),
    ("posted_ts","TIMESTAMP","N","transaction.postingDateTime",None,"financial","payments hub"),
]),

"secProperty": ("security_id", [
    ("security_id","STRING","N",None,None,"financial","collateral"),
    ("title_reference","STRING","N",None,"state titles registry","reference","collateral"),
    ("jurisdiction","STRING","N",None,"state land title jurisdiction","reference","collateral"),
    ("address_gnaf_pid","STRING","Y",None,"Geoscape G-NAF","pii","address validation"),
    ("valuation_amount","DECIMAL(18,2)","N",None,"APS 112 LVR input","financial","valuation"),
    ("valuation_date","DATE","N",None,None,"financial","valuation"),
    ("property_type","STRING","N",None,"ARS 701.0 security type","regulatory","collateral"),
]),

"lmi": ("lmi_policy_id", [
    ("lmi_policy_id","STRING","N",None,None,"financial","lending"),
    ("facility_id","STRING","N",None,None,"reference","lending"),
    ("underwriter","STRING","N",None,"APRA GPS regulated insurer","reference","lending"),
    ("insured_party","STRING","N",None,"insured is the lender","regulatory","lending"),
    ("premium_amount","DECIMAL(18,2)","N",None,None,"financial","lending"),
    ("premium_payer","STRING","N",None,"borrower pays","regulatory","lending"),
    ("capitalised_ind","BOOLEAN","N",None,None,"financial","lending"),
]),

"schemeGuar": ("scheme_guarantee_id", [
    ("scheme_guarantee_id","STRING","N",None,None,"financial","lending"),
    ("facility_id","STRING","N",None,None,"reference","lending"),
    ("scheme_name","STRING","N",None,"Housing Australia","regulatory","scheme portal"),
    ("guarantee_pct","DECIMAL(5,2)","N",None,"up to 15% of value","regulatory","scheme portal"),
    ("displaces_lmi_ind","BOOLEAN","N",None,None,"regulatory","lending"),
    ("eligibility_certificate_id","STRING","N",None,None,"reference","scheme portal"),
]),

"consent": ("consent_id", [
    ("consent_id","STRING","N","arrangementId",None,"sensitive","CDR gateway"),
    ("customer_party_id","STRING","N",None,None,"pii","CDR gateway"),
    ("adr_id","STRING","N","accreditationNumber",None,"reference","CDR Register"),
    ("scopes","ARRAY<STRING>","N","scopes",None,"sensitive","CDR gateway"),
    ("granted_ts","TIMESTAMP","N",None,"CDR Rules","regulatory","CDR gateway"),
    ("expiry_ts","TIMESTAMP","N","sharingExpiresAt","CDR Rules","regulatory","CDR gateway"),
    ("revoked_ts","TIMESTAMP","Y",None,"CDR Rules","regulatory","CDR gateway"),
]),

"amlAlert": ("alert_id", [
    ("alert_id","STRING","N",None,None,"sensitive","AML engine"),
    ("subject_party_id","STRING","N",None,None,"sensitive","AML engine"),
    ("trigger_payment_id","STRING","Y",None,None,"sensitive","AML engine"),
    ("typology","STRING","N",None,"AUSTRAC typology","sensitive","AML engine"),
    ("smr_lodged_ind","BOOLEAN","N",None,"SMR 3 business days / 24h TF","regulatory","AML engine"),
    ("tipping_off_restricted_ind","BOOLEAN","N",None,"AML/CTF Act s123","sensitive","AML engine"),
]),

"hardship": ("hardship_id", [
    ("hardship_id","STRING","N",None,None,"sensitive","hardship"),
    ("facility_id","STRING","N",None,None,"reference","hardship"),
    ("notice_received_date","DATE","N",None,"National Credit Code timeframes","regulatory","hardship"),
    ("arrangement_type","STRING","N",None,"CR Code temporary vs variation FHA","regulatory","hardship"),
    ("fhi_reported_ind","BOOLEAN","N",None,"Privacy Act Part IIIA","regulatory","credit reporting"),
    ("counsellor_authority_ind","BOOLEAN","N",None,None,"sensitive","hardship"),
]),

"product": ("product_id", [
    ("product_id","STRING","N","product.productId",None,"reference","product catalogue"),
    ("brand_id","STRING","N","product.brand",None,"reference","product catalogue"),
    ("product_category","STRING","N","product.productCategory",None,"reference","product catalogue"),
    ("name","STRING","N","product.name",None,"reference","product catalogue"),
    ("effective_from","DATETIME","N","product.effectiveFrom",None,"reference","product catalogue"),
    ("effective_to","DATETIME","Y","product.effectiveTo",None,"reference","product catalogue"),
    ("cdr_scope_status","STRING","N",None,"CDR mandatory/voluntary/out","regulatory","internal"),
    ("tmd_id","STRING","Y",None,"ASIC RG 274","regulatory","product governance"),
]),

"efs": ("return_id", [
    ("return_id","STRING","N",None,None,"regulatory","reg reporting"),
    ("arf_form","STRING","N",None,"ARF 720/741/743/747 etc","regulatory","reg reporting"),
    ("reporting_period","DATE","N",None,"APRA Connect","regulatory","reg reporting"),
    ("submitted_ts","TIMESTAMP","Y",None,None,"regulatory","reg reporting"),
    ("resubmission_ind","BOOLEAN","N",None,None,"regulatory","reg reporting"),
]),
}
