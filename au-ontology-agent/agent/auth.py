"""OAuth 2.1 resource-server checks, per MCP authorization spec 2025-11-25.

The MCP server is a resource server only. It validates tokens; it never issues
them. Pin your implementation to a spec revision - the spec changed materially
between 2025-06-18, 2025-11-25 and the 2026-07-28 draft.
"""
from __future__ import annotations
from dataclasses import dataclass

SPEC_REVISION = "2025-11-25"


@dataclass
class TokenClaims:
    sub: str
    aud: str | list[str]
    scope: str = ""
    actor_kind: str = "agent"   # agent | human


class AuthError(Exception):
    pass


class ResourceServer:
    """Audience validation is the control that stops token replay across servers
    (RFC 8707). Without it, a token minted for another MCP server works here."""

    def __init__(self, canonical_uri: str, required_scopes: dict[str, str] | None = None):
        self.canonical_uri = canonical_uri
        self.required_scopes = required_scopes or {}

    def protected_resource_metadata(self) -> dict:
        """RFC 9728. Clients fetch this to discover the authorization server."""
        return {
            "resource": self.canonical_uri,
            "authorization_servers": ["<your-as-issuer>"],
            "bearer_methods_supported": ["header"],
            "scopes_supported": sorted(set(self.required_scopes.values())),
            "mcp_spec_revision": SPEC_REVISION,
        }

    def validate(self, claims: TokenClaims, tool: str) -> None:
        aud = claims.aud if isinstance(claims.aud, list) else [claims.aud]
        if self.canonical_uri not in aud:
            raise AuthError("token audience does not match this resource (RFC 8707)")
        need = self.required_scopes.get(tool)
        if need and need not in claims.scope.split():
            raise AuthError(f"tool {tool} requires scope {need}")

    def assert_human(self, claims: TokenClaims, tool: str) -> None:
        """Write and approval tools require a human principal. Segregation of
        duties is enforced at the token, not just in the audit log."""
        if claims.actor_kind != "human":
            raise AuthError(f"{tool} requires a human principal; got {claims.actor_kind}")


READ_ONLY_TOOLS = {
    "describe_ontology", "find_class", "get_scenario", "scenarios_for_bank",
    "scenarios_for_regulator", "neighbours", "unverified_report", "run_gate",
    "list_staged", "applies_on",
}
WRITE_TOOLS = {"propose_delta"}        # agent may call: stages only, never merges
HUMAN_ONLY_TOOLS = {"approve_delta", "merge_staged", "rollback"}
