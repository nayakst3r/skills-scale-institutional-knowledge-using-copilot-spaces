# /plumbline rules [list | add | tune | disable] [change]

Edit the gate's rules in `plumbline.toml` (policy as code). Read `editing.md` first.

## list
Run `plumbline rules` and show the table (id, severity, state, title). Briefly explain any the user asks about.

## add — a team coding standard as a custom rule
1. Turn the standard into something a regex can detect on a single line. If it can't be (it needs semantics),
   say so and add it to `AGENTS.md` / the review rubric instead.
2. Append:
   ```toml
   [[plumbline.custom_rules]]
   id = "TEAM00N"            # next free id; never reuse PLxxx
   title = "<short name>"
   pattern = '<python regex>'
   message = "<what to do instead, and why — cite ARCHITECTURE.md / AGENTS.md section>"
   severity = "warn"         # start at warn; promote to error once clean
   paths = ["src/**"]
   exclude_paths = []
   ```
3. **Prove it**: write a temporary file that should match and one that shouldn't, run
   `plumbline check --files <both>`, confirm only the bad one fires, delete them.
4. Run `plumbline check --all` and report how many existing hits the new rule finds. If many, keep `warn` or
   baseline them (`plumbline check --all --write-baseline`) — ask which.

## tune
Thresholds: `fail_on`, `min_score`, `max_changed_lines`, `max_comment_ratio`, `max_modules_per_change`,
`require_tests_for`, `test_globs`, `exclude`, `severity_overrides`, `require_ai_trailer`, `required_docs`,
`extra_banned_phrases`, `provided_packages` (runtime-provided imports for PL006), `duplicate_exclude` (paths PL007
skips), `ai_trailer_key` (e.g. `Assisted-by`). Before changing, run the gate with the old and new value and tell the user the difference
in findings.

## disable
Prefer narrowing (`exclude_paths`, `severity_overrides` to `info`) over disabling. If disabling, add it to
`disabled_rules` with a TOML comment giving the reason and date. Never disable PL001, PL013 or PL014 without the
user explicitly confirming the risk.
