# /plumbline ci [add | update | explain] [job]

Add or change CI while keeping protected-main consistent. Read `editing.md` first (branch `ci/<slug>`).
Detect the platform: `.github/workflows/` → GitHub Actions; `pipelines/*.azure-pipelines.yml` or
`azure-pipelines.yml` → Azure DevOps; `.gitlab-ci.yml` → GitLab.

## Jobs you can add
| Job | What it does |
|---|---|
| `test` | Runs the stack's test suite (from the Makefile `test` target) on PRs and `main` |
| `lint` | Stack linter/formatter check (ruff / eslint / dotnet format) — only tools already in the manifest |
| `deps` | Dependency review / audit (GitHub `actions/dependency-review-action`; `npm audit`; `pip-audit`) |
| `sast` | CodeQL (GitHub) or the platform's built-in SAST |
| `gate` | Plumbline gate (`plumbline-gate`) — normally already present |
| `ai-review` | AI architecture review (`ai-architecture-review`) — normally already present |
| custom | Anything the user describes |

## add / update
1. Read existing workflows first; extend them rather than creating duplicates.
2. Write the job with:
   - least-privilege `permissions:` per workflow
   - actions pinned to a major version tag at minimum (prefer full commit SHA for third-party actions);
     only use actions and inputs you have verified exist — check the action's README if unsure
   - an explicit job `name:` (this is the status-check name)
   - the stack's real commands, the same ones as the Makefile, so local and CI agree
3. If the job should block merges, add its `name` to `required_status_checks` in
   `.github/rulesets/main-protection.json` and tell the user to re-run `/plumbline protect`. If a job is renamed
   or removed, update the ruleset in the same PR, or merging will be blocked forever.
4. Validate: YAML parses (`python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" <file>` if PyYAML is
   available), `plumbline doctor` shows required checks matching job names.
5. Update `CONTRIBUTING.md` "Pull requests" if the merge requirements changed.

## explain
Read-only. Summarise each workflow: trigger, jobs, which are required for merge, secrets used, and any gaps
(no tests on PRs, missing permissions block, unpinned actions, required checks with no matching job).
