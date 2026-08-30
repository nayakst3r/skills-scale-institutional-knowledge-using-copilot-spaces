# Ingesting prompt output

    from agent.model import Provenance, Tier
    from agent.change_policy import route
    from agent.audit import AuditLog

    for delta in prompt_output["deltas"]:
        r = route(delta["kind"], delta["body"], delta["tier"], delta["confidence"])
        AuditLog().append("propose", "research-agent@v1", "agent",
                          {"target": delta["target"], **r})
        # r["route"] is auto-merge | human-review | review-board

## Rules

- Prompt output is **tier 2 at best**, because it is model-extracted from
  unstructured sources. It proposes; it never asserts.
- Anything the prompt marks `validated` should be downgraded to `notVerified`
  on ingestion unless a tier 1 source corroborates it. Agents do not get to
  grade their own work.
- Every delta needs a source URL. No URL, no ingestion.
- Run the gate after every batch. A batch that breaks a scenario traversal is
  rejected whole, not partially applied.
