// Plumbline pre-commit hook: branch protection, forbidden and oversized files, conflict markers, custom checks.
import { context, hasCommits, loadPolicy, matchesAny, repoRoot, report, stagedSizeBytes } from "./lib.mts";

const root = repoRoot();
const policy = await loadPolicy(root);
const ctx = context("pre-commit", root);
const problems: string[] = [];

if (policy.protectedBranches.includes(ctx.branch) && hasCommits(root)) {
  problems.push(`You're on the protected branch '${ctx.branch}'. Work on a feature branch: ` +
    "`plumbline worktree new <issue>`, then open a pull request for human review.");
}

for (const file of ctx.stagedFiles) {
  if (matchesAny(file, policy.forbiddenFiles) && !matchesAny(file, policy.allowedFiles)) {
    problems.push(`'${file}' must never be committed (secrets/keys). Unstage it: git restore --staged ${file}`);
    continue;
  }
  const kb = stagedSizeBytes(root, file) / 1024;
  if (kb > policy.maxFileSizeKb) {
    problems.push(`'${file}' is ${Math.round(kb)} KB (limit ${policy.maxFileSizeKb} KB). Use Git LFS or keep it out of the repo.`);
    continue;
  }
  if (policy.blockConflictMarkers) {
    const text = ctx.readStaged(file);
    if (!text.includes("\0") && /^(<{7}|>{7}) /m.test(text)) {
      problems.push(`'${file}' contains merge conflict markers.`);
    }
  }
}

for (const check of policy.checks.preCommit) problems.push(...(await check(ctx)));
report("pre-commit", problems);
