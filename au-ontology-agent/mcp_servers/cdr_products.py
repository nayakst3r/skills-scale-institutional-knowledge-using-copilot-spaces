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

# x-v is per endpoint, not global - the three endpoints below version
# independently and are, as of this writing, three versions apart (2, 5, 7).
# A single shared header value goes stale the moment any one of them revs.
#
# Source: ConsumerDataStandardsAustralia/standards @ master, retrieved
# 2026-08-30 - swagger-gen/api/cds_register.json (operationId
# getDataHolderBrandsSummary, x-version 2), swagger-gen/api/cds_banking.json
# (operationId listBankingProducts, x-version 5; getBankingProductDetail,
# x-version 7), cross-checked against docs/includes/endpoint-version-schedule.
# x-min-v is pinned to x-v on each: the prior version of every one of these
# endpoints is already retired (Get Products v4 retired 2026-08-10, Get
# Product Detail v6 retired 2026-08-10), so there is no live fallback version
# to advertise. Confirm against a live response before trusting this past
# whenever this file was last touched - versions move on their own schedule
# and this sandbox has never reached a live data holder to verify it.
_COMMON = {"Accept": "application/json", "User-Agent": "au-bank-ontology-agent/1.0"}
REGISTER_HEADERS = {**_COMMON, "x-v": "2"}
PRODUCTS_HEADERS = {**_COMMON, "x-v": "5", "x-min-v": "5"}
PRODUCT_DETAIL_HEADERS = {**_COMMON, "x-v": "7", "x-min-v": "7"}
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
        r = await c.get(REGISTER, headers=REGISTER_HEADERS)
        r.raise_for_status()
        return _stamp(REGISTER, r.json())


@server.tool()
async def get_products(public_base_uri: str, page_size: int = 100,
                       page: int = 1) -> dict:
    """Product reference data for one brand. public_base_uri comes from the
    register. Unauthenticated - no consent required for product data."""
    url = public_base_uri.rstrip("/") + "/cds-au/v1/banking/products"
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.get(url, headers=PRODUCTS_HEADERS,
                        params={"page-size": page_size, "page": page})
        r.raise_for_status()
        return _stamp(url, r.json())


@server.tool()
async def get_product_detail(public_base_uri: str, product_id: str) -> dict:
    """Full detail for one product: features, fees, rates, eligibility, bundles."""
    url = f'{public_base_uri.rstrip("/")}/cds-au/v1/banking/products/{product_id}'
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.get(url, headers=PRODUCT_DETAIL_HEADERS)
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
