# /plumbline doctor

1. Run `plumbline doctor --json` and parse it.
2. Show results as a compact list: ✓ ok, ! warning, ✗ failure, each with its detail.
3. For each failure or warning, propose the fix, grouped:
   - Unfinished/missing docs → `/plumbline architecture` or the relevant `policy` / `agents` command
   - Vendored gate outdated → `plumbline init` (updates `.plumbline/plumbline.py`, keeps your files)
   - Git hooks inactive → `make setup`
   - CODEOWNERS drift → `plumbline codeowners`
   - Required checks don't match job names → `/plumbline ci update`
   - Missing CI → `/plumbline ci add`
4. Ask which to fix, apply them (following `editing.md` for shared-context files), and re-run doctor.
