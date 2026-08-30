"""Second curated pass. Extends agent.attributes.SPEC across every group.

Same tuple shape: (name, type, nullable Y/N, cdr_field, efs/regulatory dimension,
classification, source_system)
"""
from __future__ import annotations

V = [("valid_from","DATE","N",None,None,"regulatory","core banking"),
     ("valid_to","DATE","Y",None,None,"regulatory","core banking")]

EXT: dict[str, tuple[str, list]] = {

# ---------- party ----------
"legalEntity": ("legal_entity_id", [
 ("legal_entity_id","STRING","N",None,None,"reference","ABN Lookup"),
 ("lei","STRING","Y",None,"ISO 17442","reference","GLEIF"),
 ("abn","STRING","Y",None,None,"reference","ABN Lookup"),
 ("acn","STRING","Y",None,None,"reference","ASIC register"),
 ("entity_status","STRING","N",None,None,"reference","ASIC register"),
 ("gst_registered_ind","BOOLEAN","N",None,"ATO","regulatory","ABN Lookup")]),
"trust": ("trust_id", [
 ("trust_id","STRING","N",None,None,"reference","core banking"),
 ("trust_name","STRING","N",None,None,"pii","core banking"),
 ("trust_type","STRING","N",None,None,"reference","core banking"),
 ("deed_sighted_ind","BOOLEAN","N",None,"AML/CTF trust CDD","regulatory","KYC platform"),
 ("beneficiary_class","STRING","Y",None,None,"sensitive","KYC platform")]),
"smsf": ("smsf_id", [
 ("smsf_id","STRING","N",None,None,"reference","core banking"),
 ("abn","STRING","N",None,None,"reference","ABN Lookup"),
 ("trustee_structure","STRING","N",None,"SIS Act","regulatory","KYC platform"),
 ("ato_regulated_ind","BOOLEAN","N",None,"ATO SMSF register","regulatory","ATO"),
 ("lrba_permitted_ind","BOOLEAN","N",None,"SIS Act s67A from 10 Aug 2026","regulatory","lending")]),
"estate": ("estate_id", [
 ("estate_id","STRING","N",None,None,"sensitive","deceased estates"),
 ("deceased_party_id","STRING","N",None,None,"pii","deceased estates"),
 ("date_of_death","DATE","N",None,None,"sensitive","deceased estates"),
 ("probate_sighted_ind","BOOLEAN","N",None,"ABA Code B8","regulatory","deceased estates"),
 ("notified_date","DATE","N",None,"ABA Code B8 timeframes","regulatory","deceased estates")]),
"coreSystem": ("core_system_id", [
 ("core_system_id","STRING","N",None,None,"reference","internal"),
 ("platform_name","STRING","N",None,None,"reference","internal"),
 ("vendor","STRING","N",None,"CPS 230 material service provider","regulatory","procurement"),
 ("criticality","STRING","N",None,"CPS 230 critical operation","regulatory","GRC"),
 ("ledger_of_record_ind","BOOLEAN","N",None,None,"reference","internal")]),
"digitalId": ("digital_id_id", [
 ("digital_id_id","STRING","N",None,None,"pii","identity"),
 ("provider","STRING","N",None,"ConnectID","reference","identity"),
 ("assurance_level","STRING","N",None,"TDIF / AML CDD","regulatory","identity"),
 ("verified_ts","TIMESTAMP","N",None,None,"pii","identity")]),

# ---------- roles ----------
"acctHolder": ("account_holder_role_id", [
 ("account_holder_role_id","STRING","N",None,None,"reference","CRM"),
 ("party_id","STRING","N",None,None,"pii","CRM"),
 ("segment","STRING","N",None,None,"reference","CRM"),
 ("brand_id","STRING","N",None,None,"reference","CRM"),
 ("relationship_start","DATE","N",None,None,"reference","CRM"),
 ("depositor_sector","STRING","N",None,"ARF 747 household/business/community","regulatory","core banking")] + V),
"broker": ("broker_id", [
 ("broker_id","STRING","N",None,None,"reference","broker portal"),
 ("acl_number","STRING","Y",None,"NCCP credit licence","regulatory","ASIC register"),
 ("credit_rep_number","STRING","Y",None,"NCCP credit representative","regulatory","ASIC register"),
 ("aggregator_id","STRING","N",None,None,"reference","broker portal"),
 ("accreditation_status","STRING","N",None,None,"reference","broker portal"),
 ("bid_attested_ind","BOOLEAN","N",None,"NCCP Part 3-5A best interests duty","regulatory","broker portal"),
 ("industry_body","STRING","N",None,"MFAA / FBAA","reference","broker portal")]),
"aggregator": ("aggregator_id", [
 ("aggregator_id","STRING","N",None,None,"reference","broker portal"),
 ("name","STRING","N",None,None,"reference","broker portal"),
 ("panel_agreement_id","STRING","N",None,None,"reference","legal"),
 ("commission_model","STRING","N",None,None,"financial","finance"),
 ("acl_number","STRING","Y",None,"NCCP credit licence","regulatory","ASIC register")]),
"accountable": ("accountable_person_id", [
 ("accountable_person_id","STRING","N",None,"FAR register","regulatory","GRC"),
 ("employee_id","STRING","N",None,None,"pii","HR"),
 ("accountability_statement_id","STRING","N",None,"FAR","regulatory","GRC"),
 ("registered_with_apra_ind","BOOLEAN","N",None,"FAR","regulatory","GRC"),
 ("deferred_remuneration_pct","DECIMAL(5,2)","Y",None,"FAR / CPS 511","regulatory","HR")]),
"benefOwner": ("beneficial_owner_id", [
 ("beneficial_owner_id","STRING","N",None,None,"sensitive","KYC platform"),
 ("person_party_id","STRING","N",None,None,"pii","KYC platform"),
 ("owned_org_party_id","STRING","N",None,None,"reference","KYC platform"),
 ("ownership_pct","DECIMAL(5,2)","N",None,"AML/CTF 25% threshold","regulatory","KYC platform"),
 ("control_basis","STRING","N",None,"AML/CTF Rules","regulatory","KYC platform")]),
"msp": ("service_provider_id", [
 ("service_provider_id","STRING","N",None,None,"reference","procurement"),
 ("legal_name","STRING","N",None,None,"reference","procurement"),
 ("material_ind","BOOLEAN","N",None,"CPS 230 MSP register","regulatory","GRC"),
 ("critical_operations_supported","STRING","Y",None,"CPS 230","regulatory","GRC"),
 ("fourth_party_disclosed_ind","BOOLEAN","N",None,"CPS 230","regulatory","GRC"),
 ("register_submitted_date","DATE","Y",None,"CPS 230 register","regulatory","GRC")]),
"valuer": ("valuer_id", [
 ("valuer_id","STRING","N",None,None,"reference","valuation"),
 ("api_certified_ind","BOOLEAN","N",None,None,"reference","valuation"),
 ("panel_status","STRING","N",None,None,"reference","valuation"),
 ("valuation_basis","STRING","N",None,"APS 112 collateral valuation","regulatory","valuation")]),
"conveyancer": ("conveyancer_id", [
 ("conveyancer_id","STRING","N",None,None,"reference","settlement"),
 ("elno_subscriber_id","STRING","N",None,"ARNECC MPR","regulatory","PEXA"),
 ("jurisdiction","STRING","N",None,None,"reference","settlement")]),

# ---------- deposits ----------
"termDeposit": ("term_deposit_id", [
 ("term_deposit_id","STRING","N","account.accountId",None,"financial","core banking"),
 ("principal","DECIMAL(18,2)","N","deposit.currentBalance",None,"financial","core banking"),
 ("rate_pct","DECIMAL(6,4)","N","depositRate.rate",None,"financial","core banking"),
 ("term_months","INT","N","deposit.term",None,"reference","core banking"),
 ("maturity_date","DATE","N","deposit.maturityDate",None,"financial","core banking"),
 ("maturity_instruction","STRING","N","deposit.maturityInstructions",None,"reference","core banking"),
 ("early_withdrawal_notice_days","INT","Y",None,"ASIC DDO basic banking product","regulatory","product catalogue"),
 ("fcs_covered_ind","BOOLEAN","N",None,"Banking Act FCS","regulatory","internal")]),
"fmd": ("fmd_id", [
 ("fmd_id","STRING","N",None,None,"financial","core banking"),
 ("owner_party_id","STRING","N",None,None,"pii","core banking"),
 ("deposit_amount","DECIMAL(18,2)","N",None,"ATO FMD cap","financial","core banking"),
 ("primary_producer_ind","BOOLEAN","N",None,"ATO eligibility","regulatory","core banking"),
 ("tax_year","STRING","N",None,"ATO tax deferral","regulatory","core banking")]),
"statutoryTrust": ("statutory_trust_id", [
 ("statutory_trust_id","STRING","N",None,None,"financial","core banking"),
 ("profession","STRING","N",None,"state legal profession / agents acts","regulatory","core banking"),
 ("regulator","STRING","N",None,"state law society / fair trading","regulatory","core banking"),
 ("audit_required_ind","BOOLEAN","N",None,None,"regulatory","core banking")]),
"mandate": ("mandate_id", [
 ("mandate_id","STRING","N",None,"NPP Mandate Management Service","regulatory","payments hub"),
 ("payer_account_id","STRING","N",None,None,"financial","payments hub"),
 ("initiator_id","STRING","N",None,"ABN/ACN of initiator","reference","payments hub"),
 ("frequency","STRING","N",None,None,"reference","payments hub"),
 ("max_amount","DECIMAL(18,2)","Y",None,None,"financial","payments hub"),
 ("status","STRING","N",None,"NPP Regulations","regulatory","payments hub")]),
"fcsCover": ("fcs_cover_id", [
 ("fcs_cover_id","STRING","N",None,None,"regulatory","internal"),
 ("adi_id","STRING","N",None,"per ADI not per brand","regulatory","internal"),
 ("account_holder_party_id","STRING","N",None,None,"pii","internal"),
 ("aggregated_balance","DECIMAL(18,2)","N",None,"$250,000 cap","financial","internal"),
 ("joint_split_applied_ind","BOOLEAN","N",None,"equal split for joint accounts","regulatory","internal")]),

# ---------- credit ----------
"split": ("split_id", [
 ("split_id","STRING","N",None,None,"financial","lending"),
 ("facility_id","STRING","N",None,None,"reference","lending"),
 ("rate_type","STRING","N","lendingRate.lendingRateType","ARS 701.0 rate type","regulatory","lending"),
 ("balance","DECIMAL(18,2)","N",None,None,"financial","lending"),
 ("fixed_term_end","DATE","Y",None,None,"financial","lending")]),
"guaranteeAgr": ("guarantee_id", [
 ("guarantee_id","STRING","N",None,None,"financial","lending"),
 ("guarantor_party_id","STRING","N",None,None,"pii","lending"),
 ("supported_facility_id","STRING","N",None,None,"reference","lending"),
 ("limited_amount","DECIMAL(18,2)","Y",None,None,"financial","lending"),
 ("code_warning_given_ind","BOOLEAN","N",None,"ABA Code B6","regulatory","lending"),
 ("cooling_off_expiry","DATE","Y",None,"ABA Code B6","regulatory","lending")]),
"creditLimit": ("credit_limit_id", [
 ("credit_limit_id","STRING","N",None,None,"financial","cards"),
 ("card_account_id","STRING","N",None,None,"reference","cards"),
 ("limit_amount","DECIMAL(18,2)","N",None,"APS 112 undrawn exposure","financial","cards"),
 ("last_increase_consent_date","DATE","Y",None,"NCCP unsolicited increase ban","regulatory","cards"),
 ("assessment_id","STRING","Y",None,"responsible lending","regulatory","credit decisioning")]),
"instalment": ("instalment_plan_id", [
 ("instalment_plan_id","STRING","N",None,None,"financial","cards"),
 ("principal","DECIMAL(18,2)","N",None,None,"financial","cards"),
 ("instalment_count","INT","N",None,None,"reference","cards"),
 ("monthly_fee","DECIMAL(10,2)","N",None,None,"financial","cards"),
 ("lccc_ind","BOOLEAN","N",None,"National Credit Code low cost credit contract","regulatory","product governance")]),
"chattel": ("chattel_mortgage_id", [
 ("chattel_mortgage_id","STRING","N",None,None,"financial","asset finance"),
 ("facility_id","STRING","N",None,None,"reference","asset finance"),
 ("collateral_description","STRING","N",None,None,"reference","asset finance"),
 ("ppsr_registration_number","STRING","N",None,"PPSA registration","regulatory","PPSR"),
 ("registration_ts","TIMESTAMP","N",None,"PPSA priority timing","regulatory","PPSR")]),
"securitisation": ("securitisation_trust_id", [
 ("securitisation_trust_id","STRING","N",None,None,"financial","treasury"),
 ("pool_balance","DECIMAL(18,2)","N",None,"APS 120","financial","treasury"),
 ("capital_relief_ind","BOOLEAN","N",None,"APS 120","regulatory","treasury"),
 ("servicer_retained_ind","BOOLEAN","N",None,None,"reference","treasury")]),

# ---------- markets / wealth ----------
"isda": ("isda_id", [
 ("isda_id","STRING","N",None,None,"reference","treasury"),
 ("counterparty_party_id","STRING","N",None,None,"reference","treasury"),
 ("governing_law","STRING","N",None,None,"regulatory","legal"),
 ("csa_attached_ind","BOOLEAN","N",None,"CPS 226 margining","regulatory","treasury"),
 ("netting_opinion_held_ind","BOOLEAN","N",None,"APS 112 netting recognition","regulatory","legal")]),
"marginLoan": ("margin_loan_id", [
 ("margin_loan_id","STRING","N",None,None,"financial","wealth"),
 ("holder_party_id","STRING","N",None,None,"pii","wealth"),
 ("lvr_pct","DECIMAL(5,2)","N",None,"ARF 723 margin lending","financial","wealth"),
 ("margin_call_threshold_pct","DECIMAL(5,2)","N",None,None,"financial","wealth"),
 ("ddo_exempt_ind","BOOLEAN","N",None,"RG 274 margin loans excepted","regulatory","product governance")]),
"wrapAccount": ("wrap_account_id", [
 ("wrap_account_id","STRING","N",None,None,"financial","wealth platform"),
 ("adviser_id","STRING","Y",None,None,"reference","wealth platform"),
 ("cma_settlement_account_id","STRING","N",None,None,"reference","wealth platform"),
 ("rse_licensee","STRING","Y",None,"SIS Act where super","regulatory","wealth platform")]),
"consentless": ("x", []),

# ---------- insurance ----------
"insurancePolicy": ("policy_id", [
 ("policy_id","STRING","N",None,None,"financial","insurance"),
 ("line_of_business","STRING","N",None,None,"reference","insurance"),
 ("underwriter","STRING","N",None,"APRA GPS/LPS regulated","regulatory","insurance"),
 ("distributor_afsl","STRING","N",None,"ASIC AFSL","regulatory","insurance"),
 ("tmd_id","STRING","Y",None,"ASIC RG 274","regulatory","product governance"),
 ("deferred_sales_applied_ind","BOOLEAN","N",None,"ASIC RG 275 four-day pause","regulatory","insurance")]),
"compTravel": ("comp_travel_id", [
 ("comp_travel_id","STRING","N",None,None,"financial","cards"),
 ("card_account_id","STRING","N",None,None,"reference","cards"),
 ("underwriter","STRING","N",None,"APRA GPS regulated","regulatory","insurance"),
 ("administering_agent","STRING","N",None,"AFSL agent","regulatory","insurance"),
 ("activated_ind","BOOLEAN","N",None,None,"reference","cards"),
 ("spend_trigger_met_ind","BOOLEAN","N",None,None,"financial","cards")]),
"claim": ("claim_id", [
 ("claim_id","STRING","N",None,None,"sensitive","claims"),
 ("policy_id","STRING","N",None,None,"reference","claims"),
 ("lodged_date","DATE","N",None,None,"financial","claims"),
 ("handler_afsl","STRING","N",None,"claims handling licensed since 1 Jan 2022","regulatory","claims"),
 ("outcome","STRING","Y",None,None,"sensitive","claims"),
 ("afca_referred_ind","BOOLEAN","N",None,"AFCA","regulatory","complaints")]),

# ---------- schemes ----------
"visa": ("scheme_id", [
 ("scheme_id","STRING","N",None,None,"reference","cards"),
 ("scheme_name","STRING","N",None,None,"reference","cards"),
 ("model","STRING","N",None,"four-party","regulatory","cards"),
 ("rba_designated_ind","BOOLEAN","N",None,"RBA designation","regulatory","cards"),
 ("debit_interchange_cap","STRING","N",None,"8c or 0.16% from 1 Oct 2026","regulatory","cards"),
 ("credit_interchange_cap","STRING","N",None,"0.3% consumer from 1 Oct 2026","regulatory","cards")]),
"amex": ("scheme_id", [
 ("scheme_id","STRING","N",None,None,"reference","cards"),
 ("scheme_name","STRING","N",None,None,"reference","cards"),
 ("model","STRING","N",None,"three-party: issuer, acquirer and scheme are one","regulatory","cards"),
 ("companion_card_issuance_ceased_ind","BOOLEAN","N",None,"RBA Designation No.1 of 2015","regulatory","cards"),
 ("interchange_regulated_ind","BOOLEAN","N",None,"under RBA mid-2026 consultation","regulatory","cards")]),
"ap": ("entity_id", [
 ("entity_id","STRING","N",None,None,"reference","payments"),
 ("name","STRING","N",None,None,"reference","payments"),
 ("owns","STRING","N",None,"eftpos, BPAY, NPP, ConnectID","reference","payments"),
 ("acgs_authorised_ind","BOOLEAN","N",None,"ACCC authorisation 2021","regulatory","payments")]),

# ---------- providers ----------
"helia": ("provider_id", [
 ("provider_id","STRING","N",None,None,"reference","lending"),
 ("provider_name","STRING","N",None,None,"reference","lending"),
 ("apra_regulated_ind","BOOLEAN","N",None,"APRA GPS monoline LMI insurer","regulatory","APRA register"),
 ("panel_status","STRING","N",None,None,"reference","lending")]),
"equifax": ("bureau_id", [
 ("bureau_id","STRING","N",None,None,"reference","credit decisioning"),
 ("bureau_name","STRING","N",None,None,"reference","credit decisioning"),
 ("cr_code_bound_ind","BOOLEAN","N",None,"Privacy (Credit Reporting) Code 2024","regulatory","OAIC"),
 ("score_scale","STRING","Y",None,None,"reference","credit decisioning")]),
"pexa": ("elno_id", [
 ("elno_id","STRING","N",None,None,"reference","settlement"),
 ("elno_name","STRING","N",None,None,"reference","settlement"),
 ("arnecc_approved_ind","BOOLEAN","N",None,"ARNECC Model Operating Requirements","regulatory","ARNECC"),
 ("material_service_provider_ind","BOOLEAN","N",None,"CPS 230","regulatory","GRC")]),

# ---------- bodies ----------
"apra": ("regulator_id", [
 ("regulator_id","STRING","N",None,None,"reference","GRC"),
 ("name","STRING","N",None,None,"reference","GRC"),
 ("instruments_administered","STRING","N",None,"CPS/APS/CPG standards, ARF returns","regulatory","GRC"),
 ("reporting_channel","STRING","N",None,"APRA Connect","regulatory","reg reporting"),
 ("incident_notification_hours","INT","N",None,"CPS 230: 72h material, 24h critical","regulatory","GRC")]),
"austrac": ("regulator_id", [
 ("regulator_id","STRING","N",None,None,"reference","GRC"),
 ("name","STRING","N",None,None,"reference","GRC"),
 ("report_types","STRING","N",None,"SMR, TTR, IFTI","regulatory","AML engine"),
 ("smr_deadline_days","INT","N",None,"3 business days; 24h terrorism financing","regulatory","AML engine"),
 ("ttr_threshold","DECIMAL(18,2)","N",None,"$10,000 physical cash","regulatory","AML engine")]),

# ---------- loyalty ----------
"loyaltyProgram": ("loyalty_program_id", [
 ("loyalty_program_id","STRING","N",None,None,"reference","loyalty"),
 ("program_name","STRING","N",None,None,"reference","loyalty"),
 ("points_currency","STRING","N",None,None,"reference","loyalty"),
 ("open_to_new_customers_ind","BOOLEAN","N",None,None,"reference","loyalty"),
 ("tmd_id","STRING","Y",None,"ASIC RG 274 card feature","regulatory","product governance"),
 ("change_notice_days","INT","Y",None,"ACCC loyalty review recommendation","regulatory","loyalty")]),
"transferPartner": ("transfer_partner_id", [
 ("transfer_partner_id","STRING","N",None,None,"reference","loyalty"),
 ("partner_name","STRING","N",None,None,"reference","loyalty"),
 ("partner_type","STRING","N",None,"airline / coalition","reference","loyalty"),
 ("conversion_ratio","STRING","N",None,None,"financial","loyalty"),
 ("transfer_minimum","INT","N",None,None,"financial","loyalty"),
 ("bonus_window","STRING","Y",None,None,"financial","loyalty")]),
"merchantOffer": ("offer_id", [
 ("offer_id","STRING","N",None,None,"financial","loyalty"),
 ("merchant_party_id","STRING","N",None,None,"reference","loyalty"),
 ("funding_party","STRING","N",None,"merchant funded","financial","loyalty"),
 ("targeting_platform","STRING","N",None,"card network offers engine","regulatory","loyalty"),
 ("personal_info_shared_ind","BOOLEAN","N",None,"Privacy Act / OAIC","sensitive","privacy"),
 ("activation_required_ind","BOOLEAN","N",None,None,"reference","loyalty")]),

# ---------- events ----------
"cardTxn": ("card_txn_id", [
 ("card_txn_id","STRING","N","transaction.transactionId",None,"financial","cards"),
 ("card_account_id","STRING","N",None,None,"reference","cards"),
 ("merchant_category_code","STRING","N",None,None,"reference","cards"),
 ("amount","DECIMAL(18,2)","N","transaction.amount",None,"financial","cards"),
 ("network_routed","STRING","N",None,"least-cost routing outcome","regulatory","cards"),
 ("interchange_amount","DECIMAL(10,4)","Y",None,"RBA Standard No.1","financial","cards"),
 ("surcharge_amount","DECIMAL(10,2)","Y",None,"removed from 1 Oct 2026","regulatory","cards"),
 ("wallet_token_ind","BOOLEAN","N",None,None,"reference","cards")]),
"kyc": ("kyc_review_id", [
 ("kyc_review_id","STRING","N",None,None,"sensitive","KYC platform"),
 ("party_id","STRING","N",None,None,"pii","KYC platform"),
 ("review_type","STRING","N",None,"onboarding / periodic / trigger","regulatory","KYC platform"),
 ("risk_rating","STRING","N",None,"AML/CTF customer risk","sensitive","KYC platform"),
 ("verified_ts","TIMESTAMP","N",None,"AML/CTF CDD","regulatory","KYC platform"),
 ("ecdd_applied_ind","BOOLEAN","N",None,"enhanced CDD for PEP/high risk","regulatory","KYC platform")]),
"complaint": ("complaint_id", [
 ("complaint_id","STRING","N",None,None,"sensitive","complaints"),
 ("complainant_party_id","STRING","Y",None,None,"pii","complaints"),
 ("received_date","DATE","N",None,"RG 271 timeframes","regulatory","complaints"),
 ("product_code","STRING","N",None,"RG 271 IDR data schema","regulatory","complaints"),
 ("issue_code","STRING","N",None,"RG 271 IDR data schema","regulatory","complaints"),
 ("outcome_code","STRING","Y",None,"RG 271 IDR data schema","regulatory","complaints"),
 ("afca_referred_ind","BOOLEAN","N",None,"AFCA Rules","regulatory","complaints")]),
"settlement": ("settlement_id", [
 ("settlement_id","STRING","N",None,None,"financial","settlement"),
 ("workspace_id","STRING","N",None,"ELNO workspace","reference","PEXA"),
 ("scheduled_ts","TIMESTAMP","N",None,None,"financial","settlement"),
 ("duty_assessed_amount","DECIMAL(18,2)","Y",None,"state revenue office","regulatory","settlement"),
 ("title_dealing_number","STRING","Y",None,"state titles registry","regulatory","settlement")]),
"scamReport": ("scam_report_id", [
 ("scam_report_id","STRING","N",None,None,"sensitive","fraud"),
 ("payment_id","STRING","N",None,None,"reference","payments hub"),
 ("reported_ts","TIMESTAMP","N",None,"Scams Prevention Framework","regulatory","fraud"),
 ("recall_attempted_ind","BOOLEAN","N",None,"ePayments Code","regulatory","payments hub"),
 ("reimbursed_amount","DECIMAL(18,2)","Y",None,"SPF sector code","financial","fraud"),
 ("receiving_institution","STRING","Y",None,"AFCA rules extend to receiving bank","regulatory","payments hub")]),

# ---------- assets ----------
"ppsr": ("ppsr_registration_id", [
 ("ppsr_registration_id","STRING","N",None,"PPSA","regulatory","PPSR"),
 ("collateral_class","STRING","N",None,"PPSA collateral class","regulatory","PPSR"),
 ("grantor_identifier","STRING","N",None,"ABN or ACN or DOB","pii","PPSR"),
 ("registration_ts","TIMESTAMP","N",None,"PPSA priority","regulatory","PPSR"),
 ("expiry_date","DATE","N",None,None,"regulatory","PPSR")]),
"title": ("title_id", [
 ("title_id","STRING","N",None,None,"reference","collateral"),
 ("volume_folio","STRING","N",None,"state format varies","reference","titles registry"),
 ("jurisdiction","STRING","N",None,"eight registries, eight formats","regulatory","titles registry"),
 ("mortgage_registered_ind","BOOLEAN","N",None,"registration makes security enforceable","regulatory","titles registry")]),

# ---------- place ----------
"address": ("address_id", [
 ("address_id","STRING","N",None,None,"pii","address validation"),
 ("gnaf_pid","STRING","Y",None,"Geoscape G-NAF","pii","address validation"),
 ("as4590_compliant_ind","BOOLEAN","N",None,"AS4590","reference","address validation"),
 ("state","STRING","N",None,None,"reference","address validation"),
 ("postcode","STRING","N",None,None,"pii","address validation"),
 ("sa2_code","STRING","Y",None,"ABS statistical geography","reference","enrichment")]),
"branch": ("branch_id", [
 ("branch_id","STRING","N",None,None,"reference","channel ops"),
 ("brand_id","STRING","N",None,None,"reference","channel ops"),
 ("address_id","STRING","N",None,None,"reference","channel ops"),
 ("regional_ind","BOOLEAN","N",None,"regional closure moratorium","regulatory","channel ops"),
 ("closure_date","DATE","Y",None,None,"regulatory","channel ops")]),

# ---------- regulatory objects ----------
"tmd": ("tmd_id", [
 ("tmd_id","STRING","N",None,"ASIC RG 274","regulatory","product governance"),
 ("product_id","STRING","N",None,None,"reference","product governance"),
 ("target_market_description","STRING","N",None,"RG 274","regulatory","product governance"),
 ("review_trigger","STRING","N",None,"RG 274 review triggers","regulatory","product governance"),
 ("next_review_date","DATE","N",None,"RG 274","regulatory","product governance"),
 ("significant_dealing_notified_ts","TIMESTAMP","Y",None,"10 business days to issuer/ASIC","regulatory","product governance")]),
"criticalOp": ("critical_operation_id", [
 ("critical_operation_id","STRING","N",None,"CPS 230","regulatory","GRC"),
 ("name","STRING","N",None,None,"reference","GRC"),
 ("tolerance_level","STRING","N",None,"CPS 230 board-approved","regulatory","GRC"),
 ("last_tested_date","DATE","N",None,"CPS 230 testing","regulatory","GRC"),
 ("accountable_person_id","STRING","N",None,"FAR","regulatory","GRC")]),
"rhi": ("rhi_id", [
 ("rhi_id","STRING","N",None,"Privacy Act Part IIIA","regulatory","credit reporting"),
 ("facility_id","STRING","N",None,None,"reference","credit reporting"),
 ("period","DATE","N",None,"monthly supply","regulatory","credit reporting"),
 ("repayment_status","STRING","N",None,"RHI code","sensitive","credit reporting"),
 ("financial_hardship_indicator","STRING","Y",None,"CR Code temporary vs variation FHA","sensitive","credit reporting")]),
"smr": ("smr_id", [
 ("smr_id","STRING","N",None,"AML/CTF Act","regulatory","AML engine"),
 ("subject_party_id","STRING","N",None,None,"sensitive","AML engine"),
 ("grounds","STRING","N",None,"suspicion formed","sensitive","AML engine"),
 ("lodged_ts","TIMESTAMP","N",None,"3 business days / 24h TF","regulatory","AML engine"),
 ("tipping_off_restricted_ind","BOOLEAN","N",None,"AML/CTF Act s123","sensitive","AML engine")]),
"idrRecord": ("idr_record_id", [
 ("idr_record_id","STRING","N",None,"ASIC Instrument 2022/205","regulatory","complaints"),
 ("complaint_id","STRING","N",None,None,"reference","complaints"),
 ("product_line","STRING","N",None,"RG 271 taxonomy","regulatory","complaints"),
 ("days_to_resolution","INT","Y",None,"RG 271 30-day maximum","regulatory","complaints"),
 ("reported_period","STRING","N",None,"biannual ASIC lodgement","regulatory","complaints")]),
}
EXT.pop("consentless", None)
