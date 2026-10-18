# /plumbline review [base-branch | PR#]

Semantic review of a change — what static rules can't see.

1. Diff: PR number → `gh pr diff <n>`; branch → `git diff <branch>...HEAD`; nothing → `git diff origin/main...HEAD`.
2. Run `plumbline check --diff <base>` first; don't repeat its findings.
3. Read `ARCHITECTURE.md`, accepted ADRs, `AGENTS.md`, and the linked issue if there is one.
4. Review against `review-rubric.md` in this folder. If your agent can start an independent sub-agent, give it the
   diff range, the rubric and the static findings, so the review isn't done by the same context that wrote the code.
5. Present: verdict (approve / approve with comments / request changes), static score, rubric score /30,
   blocking comments (file:line, problem, required change), non-blocking comments, questions for the author.
6. Offer to post it to the PR (`gh pr review`). Ask first — it is posted on the user's behalf.
