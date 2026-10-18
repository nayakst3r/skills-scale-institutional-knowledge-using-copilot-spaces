# /plumbline check [staged | all | <base-branch>]

1. Scope: `staged` → `--staged`; `all` → `--all`; a branch → `--diff <branch>`; nothing → `--diff origin/main` if
   that ref exists, else `--diff main`, else `--all`.
2. Run `plumbline check <scope> --format json` and parse it.
3. Report only:
   - one line: score, PASS/FAIL, counts by severity
   - findings grouped by rule: rule, file:line, why it matters in one clause
   - for each error, the concrete fix
4. If something looks like a false positive, say so and show the inline suppression with a reason
   (`# plumbline: ignore PL006 — vendored module`). Do not edit files here; offer `/plumbline fix`.
