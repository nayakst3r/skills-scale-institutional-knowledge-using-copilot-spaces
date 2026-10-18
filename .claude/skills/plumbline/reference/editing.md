# Editing protocol for shared-context files

Applies to `ARCHITECTURE.md`, `AGENTS.md`, `AI_POLICY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`,
`docs/adr/*`, `plumbline.toml`, `.github/**` and `CODEOWNERS`. Every engineer and agent depends on these files, so
changes are deliberate, small and reviewed.

1. **Branch.** `git fetch origin && git switch -c docs/<short-slug> origin/main` (use `ci/<slug>` for CI,
   `chore/<slug>` for rules). If the working tree is dirty, stop and ask.
2. **Read before writing.** Read the target file in full, plus every other shared-context file that might state the
   same thing. Note any statement your change would contradict.
3. **Understand the change.** If the request is ambiguous, ask at most 3 multiple-choice questions in one round.
   Do not invent organisational facts (team names, approved tools, regulators, SLAs).
4. **Edit surgically.** Keep the file's headings, order and tone. Change only what the request needs. No filler.
   Do not leave unfinished-template markers.
5. **Keep files consistent.** Update every other file that states the changed fact in the same branch
   (e.g. a newly approved AI tool appears in `AI_POLICY.md` and, if agents must behave differently, `AGENTS.md`).
6. **Architecture changes need an ADR.** If `ARCHITECTURE.md` changes after its first merge, follow `adr.md` first.
7. **Validate.**
   - `plumbline check --diff origin/main` — must pass (PL014 unfinished/missing docs, PL015 ADR, custom rules)
   - `plumbline codeowners` if module owners changed
   - `plumbline doctor` — no new failures
8. **Show the diff** to the user with a 2-3 line summary of what changed and why. Ask before committing.
9. **Commit and PR.** Conventional Commit (`docs(policy): ...`, `ci: ...`, `chore(rules): ...`) with trailers
   `AI-Assisted: yes` and `AI-Tool: <your agent>`. Push the branch and open a PR (`gh pr create --fill` if
   available), requesting review from the code owners of the changed files.
10. **Stop and hand over** with the review packet from `human-review.md`. Do not merge, approve or resolve threads.
