"""Rebuild the viewer's embedded payload from model/model.json.

The viewer embeds its own copy of the model, so it goes stale the moment the
pipeline merges a change. This is the regeneration step; CI fails if it was
not run.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    m = json.loads((ROOT / "model" / "model.json").read_text())
    slim = {
        "counts": m["counts"], "mvm": m["mvmProductIds"],
        "products": {p["classId"]: {
            "pid": p["productId"], "pk": p["primaryKey"], "detail": p["detail"],
            "tags": p["tags"],
            "a": [[a["name"], a["type"], 0 if a["nullable"] else 1,
                   1 if a["primaryKey"] else 0, a["cdrField"] or "",
                   a["efsDimension"] or "", a["classification"], a["sourceSystem"]]
                  for a in p["attributes"]]} for p in m["products"]},
        "fks": [[f["fromProduct"], f["toProduct"], f["predicateLabel"],
                 1 if f["constraint"] == "foreignKey" else 0]
                for f in m["foreignKeys"]],
    }
    payload = json.dumps(slim, separators=(",", ":"))
    (ROOT / "model" / "viewer-payload.json").write_text(payload)

    v = ROOT / "viewer" / "bank-ontology.html"
    h = v.read_text()
    start = h.index("const MODEL = ")
    end = h.index(";\nconst CLSORDER")
    v.write_text(h[:start] + "const MODEL = " + payload + h[end:])
    print(f'viewer payload refreshed: {len(slim["products"])} products, '
          f'{m["counts"]["attributes"]} attributes')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
