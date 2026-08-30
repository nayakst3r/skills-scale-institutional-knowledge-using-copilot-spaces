"""MCP server over the Consumer Data Right banking endpoints.

These are unauthenticated, standardised and published by every data holder,
which is what makes sector-wide product coverage possible without scraping.
Read-only. Every response carries the source URL and retrieval time.
"""
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
from mcp.server.mcpserver import MCPServer

REGISTER = "https://api.cdr.gov.au/cdr-register/v1/banking/data-holders/brands/summary"
HEADERS = {"x-v": "4", "x-min-v": "3", "Accept": "application/json",
           "User-Agent": "au-bank-ontology-agent/1.0"}
TIMEOUT = 30.0

server = MCPServer("au-cdr-products")


def _stamp(url: str, payload):
    return {"source": url, "tier": 1,
            "retrievedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "data": payload}


@server.tool()
async def list_data_holders() -> dict:
    """Every registered CDR banking data holder brand. This is the sector list."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.get(REGISTER, headers=HEADERS)
        r.raise_for_status()
        return _stamp(REGISTER, r.json())


@server.tool()
async def get_products(public_base_uri: str, page_size: int = 100,
                       page: int = 1) -> dict:
    """Product reference data for one brand. public_base_uri comes from the
    register. Unauthenticated - no consent required for product data."""
    url = public_base_uri.rstrip("/") + "/cds-au/v1/banking/products"
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.get(url, headers=HEADERS,
                        params={"page-size": page_size, "page": page})
        r.raise_for_status()
        return _stamp(url, r.json())


@server.tool()
async def get_product_detail(public_base_uri: str, product_id: str) -> dict:
    """Full detail for one product: features, fees, rates, eligibility, bundles."""
    url = f'{public_base_uri.rstrip("/")}/cds-au/v1/banking/products/{product_id}'
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.get(url, headers=HEADERS)
        r.raise_for_status()
        return _stamp(url, r.json())


@server.tool()
async def diff_against_ontology(brand: str, public_base_uri: str) -> dict:
    """Fetch a brand's products and report what the ontology cannot express."""
    from agent.differ import Differ
    payload = await get_products(public_base_uri)
    d = Differ(str(Path(__file__).resolve().parents[1] /
                   "ontology" / "bank-ontology.json"))
    gaps = d.diff_cdr_products(brand, payload["data"], payload["source"])
    return {"brand": brand, "source": payload["source"],
            "gapCount": len(gaps),
            "gaps": [{"kind": g.kind, "subject": g.subject, "detail": g.detail,
                      "suggested": g.suggested} for g in gaps]}


if __name__ == "__main__":
    server.run()
