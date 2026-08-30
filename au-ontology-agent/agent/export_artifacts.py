"""Emit the artefacts the Databricks repo ships alongside model.json:
schemas/ (DDL), diagram/ (DBML), metrics/ (metric view SQL), ontology/ (tag taxonomy).
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = json.loads((ROOT / "model" / "model.json").read_text())

TYPE_MAP = {"STRING":"STRING","BOOLEAN":"BOOLEAN","DATE":"DATE","TIMESTAMP":"TIMESTAMP",
            "DATETIME":"TIMESTAMP","INT":"INT","BIGINT":"BIGINT"}
def sqltype(t): return TYPE_MAP.get(t, t)

def ddl():
    out = ROOT / "model" / "schemas"; out.mkdir(parents=True, exist_ok=True)
    by_domain = {}
    for p in M["products"]:
        by_domain.setdefault(p["domain"], []).append(p)
    for dom, prods in by_domain.items():
        lines = [f"-- domain: {prods[0]['domainLabel']}",
                 f"CREATE SCHEMA IF NOT EXISTS au_banking.{dom};", ""]
        for p in prods:
            cols = []
            for a in p["attributes"]:
                c = f'  {a["name"]} {sqltype(a["type"])}'
                if not a["nullable"]: c += " NOT NULL"
                cmt = []
                if a["cdrField"]: cmt.append(f'CDR: {a["cdrField"]}')
                if a["efsDimension"]: cmt.append(f'REG: {a["efsDimension"]}')
                cmt.append(f'class: {a["classification"]}')
                cmt.append(f'source: {a["sourceSystem"]}')
                c += f' COMMENT \'{"; ".join(cmt)}\''
                cols.append(c)
            cols.append(f'  CONSTRAINT pk_{p["productId"]} PRIMARY KEY ({p["primaryKey"]})')
            lines += [f'CREATE TABLE IF NOT EXISTS au_banking.{dom}.{p["productId"]} (',
                      ",\n".join(cols),
                      f") COMMENT '{p['name']} ({p['detail']})'", "TBLPROPERTIES (",
                      f"  'au.detail' = '{p['detail']}',",
                      f"  'au.tags' = '{','.join(p['tags'])}'", ");", ""]
        for f in M["foreignKeys"]:
            src = next((x for x in prods if x["productId"] == f["fromProduct"]), None)
            if not src or f["constraint"] != "foreignKey": continue
            tgt = next(x for x in M["products"] if x["productId"] == f["toProduct"])
            lines.append(f'ALTER TABLE au_banking.{dom}.{f["fromProduct"]} ADD CONSTRAINT '
                         f'{f["name"][:60]} FOREIGN KEY ({tgt["primaryKey"]}) '
                         f'REFERENCES au_banking.{tgt["domain"]}.{f["toProduct"]};')
        (out / f"{dom}.sql").write_text("\n".join(lines) + "\n")
    return len(by_domain), sum(len(v) for v in by_domain.values())

def dbml():
    out = ROOT / "model" / "diagram"; out.mkdir(parents=True, exist_ok=True)
    L = [f'// {M["modelName"]} {M["flavour"]} — generated from the ontology',
         f'// {M["counts"]["products"]} products, {M["counts"]["attributes"]} attributes', ""]
    for p in M["products"]:
        L.append(f'Table {p["domain"]}.{p["productId"]} {{')
        for a in p["attributes"]:
            mods = []
            if a["primaryKey"]: mods.append("pk")
            if not a["nullable"]: mods.append("not null")
            note = a["cdrField"] or a["efsDimension"] or a["classification"]
            mods.append(f"note: '{note}'")
            L.append(f'  {a["name"]} {sqltype(a["type"]).lower()} [{", ".join(mods)}]')
        L.append(f'  Note: "{p["name"]} · {p["detail"]}"'); L.append("}"); L.append("")
    for f in M["foreignKeys"]:
        if f["constraint"] != "foreignKey": continue
        t = next(x for x in M["products"] if x["productId"] == f["toProduct"])
        s = next(x for x in M["products"] if x["productId"] == f["fromProduct"])
        L.append(f'Ref: {s["domain"]}.{f["fromProduct"]}.{t["primaryKey"]} > '
                 f'{t["domain"]}.{f["toProduct"]}.{t["primaryKey"]} // {f["predicateLabel"]}')
    (out / "model.dbml").write_text("\n".join(L) + "\n")
    return len(M["products"])

def metrics():
    out = ROOT / "model" / "metrics"; out.mkdir(parents=True, exist_ok=True)
    n = 0
    for mv in M["metricViews"]:
        prods = [p for p in mv["products"]
                 if any(x["productId"] == p for x in M["products"])]
        if len(prods) < 2: continue
        base = prods[0]
        dom = next(x["domain"] for x in M["products"] if x["productId"] == base)
        joins = ""
        for p in prods[1:6]:
            d = next(x["domain"] for x in M["products"] if x["productId"] == p)
            joins += f"\n  LEFT JOIN au_banking.{d}.{p} ON /* TODO: join key */ TRUE"
        sql = (f"-- {mv['label']}\n"
               f"-- scenario: {mv['scenarioId']}  |  validation: {mv['validation']}\n"
               f"-- regulatory: {'; '.join(mv['regulatoryReferences'])}\n"
               f"CREATE OR REPLACE VIEW au_banking._metrics.{mv['name']} AS\n"
               f"SELECT *\nFROM au_banking.{dom}.{base}{joins};\n")
        (out / f"{mv['name']}.sql").write_text(sql); n += 1
    return n

def tags():
    out = ROOT / "model" / "ontology"; out.mkdir(parents=True, exist_ok=True)
    tax = {}
    for p in M["products"]:
        for a in p["attributes"]:
            tax.setdefault(a["classification"], {"attributes": 0, "products": set()})
            tax[a["classification"]]["attributes"] += 1
            tax[a["classification"]]["products"].add(p["productId"])
    payload = {"taxonomy": {k: {"attributes": v["attributes"],
                                "products": len(v["products"])} for k, v in tax.items()},
               "handling": {
                 "pii": "Privacy Act APPs; masking and access control required",
                 "sensitive": "Privacy Act sensitive information; restricted access, purpose limited",
                 "regulatory": "feeds an APRA, ASIC, AUSTRAC or ATO obligation; retention per instrument",
                 "financial": "material to financial reporting; CPG 235 quality controls",
                 "reference": "shared reference data; steward-owned",
                 "derived": "computed; lineage must state the derivation"}}
    (out / "tag-taxonomy.json").write_text(json.dumps(payload, indent=2))
    return len(tax)

if __name__ == "__main__":
    d, t = ddl(); print(f"schemas/   {d} domain DDL files, {t} tables")
    print(f"diagram/   model.dbml, {dbml()} tables")
    print(f"metrics/   {metrics()} metric view SQL files")
    print(f"ontology/  tag taxonomy, {tags()} classifications")
