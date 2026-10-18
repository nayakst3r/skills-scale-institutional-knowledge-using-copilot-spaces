# /plumbline fix [scope]

1. Run the gate as in `check.md` with `--format json`.
2. Fix one rule at a time, in this order:
   - **PL001 secret**: move to env var / secret store, and tell the user to **rotate** it — it may be in history.
   - **PL006 undeclared dependency**: verify the package exists (registry or lockfile). Real and needed → pinned
     manifest entry. Not real → it was invented; rewrite with the stdlib or an existing dependency.
   - **PL013 boundary**: move the logic to the module allowed to own it, or depend on a port in an allowed module.
     Never "fix" by editing `may_import` — that is an architecture change (`/plumbline adr`).
   - **PL014 shared context**: run the relevant `architecture` / `agents` / `policy` command.
   - **PL002 stub**: implement it properly; if scope is unclear, stop and ask.
   - **PL003 / PL005 / PL011**: delete chatbot text, debug output and filler.
   - **PL009**: handle the specific exception, or log with context and re-raise.
   - **PL004**: delete comments that restate code; keep the ones that explain why.
   - **PL007**: extract the duplicate into one shared function in an allowed module.
   - **PL008**: write tests that would fail if the code were wrong; run them.
   - **PL010 / PL016**: don't edit — propose how to split the PR by module.
   - **PL017**: move the file into the right module.
   - **Custom rules**: follow the rule's message.
3. Re-run until it passes or only human decisions remain. Run `make test`.
4. Report before/after score, changes per rule, what's left for the human, test result. Never add a suppression
   without telling the user why.
