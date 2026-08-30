# Prompt pack — for platform execution

The scaffold covers structure. These prompts cover completeness. Run them on a
platform with research and long-running execution, one per domain, and feed each
result back through `propose_delta` so it lands in the review queue rather than
straight into the graph.

Every prompt must end with the same instruction block, or the output cannot be
ingested:

> Return findings as structured deltas. For each: the proposed class or
> relationship, its parent, the exact source URL, the retrieval date, the source
> tier (1 authoritative machine-readable, 2 authoritative unstructured,
> 3 bank-published, 4 secondary), and a confidence of validated or notVerified.
> Never mark your own findings validated. Flag anything you could not verify.
