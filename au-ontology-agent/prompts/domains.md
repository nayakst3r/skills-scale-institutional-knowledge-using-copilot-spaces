# Domain prompts — remaining coverage

Each returns deltas. None writes to the graph directly.

## Products and sub-products
1. **Deposits** — every transaction, savings, term deposit, concession, youth, trust and business deposit sub-product across all CDR data holders, not just the six. Source: CDR product reference data across the full brand register.
2. **Home lending** — every sub-product and feature: rate type, repayment type, package tier, LMI waiver professions, construction, bridging, portability, redraw, offset count limits.
3. **Business and asset finance** — chattel mortgage, hire purchase, finance vs operating lease, novated, fleet, invoice, supply chain, agri, franchise, professional practice.
4. **Markets and wealth** — FX, rates, commodity, credit derivatives, structured deposits and products, repo, custody, prime brokerage, wrap, super, margin, broking.
5. **Insurance** — every line, every underwriter, the distributor split, and the licence each sits under.
6. **Cards and loyalty** — earn rules, caps, exclusions, transfer partners and ratios, tier benefits, merchant-funded offers, points liability treatment.
7. **Payments** — NPP, PayTo, PayID, BPAY, BECS, cheques, RTGS, wallets, ConnectID.

## Parties
8. **The full ADI register** — every ADI, brand, NOHC, foreign parent. Source: APRA register plus the CDR brand directory.
9. **Intermediaries** — every aggregator, broker group, mortgage manager, referrer arrangement.
10. **Providers** — underwriters, LMI insurers, bureaux, ELNOs, valuers, cash logistics, identity providers.
11. **Regulators and bodies** — with the specific instrument each administers.

## Obligations
12. **APRA** — every prudential standard and reporting standard, with the products each attaches to and the ARF forms and dimensions each demands.
13. **ASIC** — every regulatory guide relevant to banking, with the licence type and product class each binds.
14. **AUSTRAC** — every designated service item mapped to product classes.
15. **Codes** — Banking Code parts, ePayments Code, General and Life Insurance Codes, Scams Prevention Framework.
16. **Validity intervals** — every dated obligation from 2024 to 2028, with commencement and end dates, so `applies_on` returns a real answer.

## Scenarios
17. **Per domain** — the scenarios each product set requires that the current 124 do not cover.
18. **Failure and edge paths** — what each scenario looks like when it goes wrong: declined, disputed, defaulted, deceased, breached.

## Attribute-level prompts

The class layer is broad; the attribute layer is thin. 74 of 366 products are
curated, 292 are stubs. These close it.

19. **Attributes per domain** — for every stub product in a given domain, return the columns a real Australian bank would hold: name, type, nullability, primary key, CDR field where one exists, APRA reporting dimension where one applies, classification (pii, sensitive, regulatory, financial, reference, derived), and source system. One prompt per domain, fifteen in total.
20. **CDR field coverage** — walk the Consumer Data Standards banking payloads (accounts, balances, transactions, direct debits, scheduled payments, payees, products, customer) field by field, and report which have no attribute in the model.
21. **APRA reporting coverage** — for each ARF form (720, 721, 722, 723, 730, 741, 742, 743, 744, 745, 746, 747), list the required data items and dimensions, and report which have no attribute carrying them.
22. **Classification review** — for every attribute already curated, challenge the classification. Under-classified PII is the failure mode that matters.
23. **Join keys** — the generated metric view SQL has `TODO: join key` placeholders. For each, name the actual join.

### Ingestion for attribute deltas

    kind:  addAttribute
    body:  {product, name, type, nullable, primaryKey, cdrField,
            efsDimension, classification, sourceSystem}

Routing: an attribute on a stub product is additive and auto-merges from a
tier 1 source. An attribute carrying a regulatory dimension or a pii/sensitive
classification touches an obligation and always goes to human review.
