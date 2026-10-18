# /plumbline spec [title]

Turn the current conversation (usually after `/plumbline grill`) into a spec and publish it as a GitHub issue **for
human approval**. No new interview: synthesise what was already decided. Inspired by Matt Pocock's `/to-spec`;
this version maps the work onto the architecture and never releases it to agents itself.

1. Re-read `ARCHITECTURE.md`, `GLOSSARY.md`, relevant ADRs and the code involved. Use glossary terms exactly.
2. **Test seams:** propose where behaviour will be tested — prefer existing seams and the highest level that's
   practical, ideally one. Confirm them with the user in one message.
3. **Architecture check:** list the modules involved. If the work needs a change to `ARCHITECTURE.md`, stop and
   say an ADR must be merged first (`/plumbline adr`); put that in the spec as a blocker.
4. Write the spec:
   ```
   ## Problem
   ## Solution                       (behaviour, from the user's point of view)
   ## User stories                   (numbered; "As a …, I want …, so that …")
   ## Modules affected               (from ARCHITECTURE.md; for each: what changes, owners)
   ## Architecture impact            ("None — within current boundaries" or the ADR that must land first)
   ## Implementation decisions       (interfaces, schema, API contracts — no file paths or code, except a short
                                      prototype snippet when it captures a decision better than prose)
   ## Testing decisions              (the agreed seams; what each test proves)
   ## Out of scope
   ## Open questions                 (from the grill; who answers each)
   ```
5. Publish: write the body to a temp file, then
   `gh issue create --title "Spec: <title>" --label spec --label needs-human-approval --body-file <file>`.
   Use the tracker in `docs/agents/issue-tracker.md` if it says otherwise. **Never** add `ready-for-agent` — the guard
   blocks it, and approving a spec is a human decision.
6. Hand over with the review packet: link, modules, open questions, and "Approve by reviewing the spec, then run
   `/plumbline tickets <number>`."
