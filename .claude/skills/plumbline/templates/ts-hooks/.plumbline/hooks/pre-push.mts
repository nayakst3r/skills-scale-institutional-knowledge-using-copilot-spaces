// Plumbline pre-push hook: never push to protected branches; feature branches follow the worktree naming.
import { context, loadPolicy, parsePushUpdates, repoRoot, report, validatePush } from "./lib.mts";

const chunks: Buffer[] = [];
for await (const chunk of process.stdin) chunks.push(chunk as Buffer);
const root = repoRoot();
const policy = await loadPolicy(root);
const problems = validatePush(parsePushUpdates(Buffer.concat(chunks).toString("utf8")), policy);
const ctx = context("pre-push", root);
for (const check of policy.checks.prePush) problems.push(...(await check(ctx)));
report("pre-push", problems);
