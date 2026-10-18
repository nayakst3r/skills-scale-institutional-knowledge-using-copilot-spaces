// Unit tests for the hook rules: node --test .plumbline/hooks/lib.test.mts
import { test } from "node:test";
import assert from "node:assert/strict";
import { DEFAULT_POLICY, defineHooks, globToRegExp, matchesAny, parseCommit, parsePushUpdates, validateCommit,
  validatePush } from "./lib.mts";

const modules = ["orders", "payments", "shared"];
const ok = "feat(orders): reject zero quantity\n\nAI-Assisted: yes\nAI-Tool: claude-code\n";

test("valid conventional commit with module scope and trailer passes", () => {
  assert.deepEqual(validateCommit(ok, DEFAULT_POLICY.commit, modules), []);
});

test("scope must be an architecture module", () => {
  const msg = "feat(billing): add invoice\n\nAI-Assisted: no\n";
  const problems = validateCommit(msg, DEFAULT_POLICY.commit, modules);
  assert.equal(problems.length, 1);
  assert.match(problems[0], /isn't a module in ARCHITECTURE\.md/);
});

test("extra scopes like deps are always allowed", () => {
  assert.deepEqual(validateCommit("chore(deps): bump zod\n\nAI-Assisted: no\n", DEFAULT_POLICY.commit, modules), []);
});

test("missing trailer, bad type and trailing full stop are reported", () => {
  const problems = validateCommit("feature(orders): Add thing.", DEFAULT_POLICY.commit, modules);
  assert.equal(problems.length, 3);
});

test("git comment lines are ignored and merges are exempt", () => {
  assert.deepEqual(validateCommit(`${ok}# Please enter the commit message\n`, DEFAULT_POLICY.commit, modules), []);
  assert.deepEqual(validateCommit("Merge branch 'main' into feat/1-x", DEFAULT_POLICY.commit, modules), []);
});

test("breaking changes are detected", () => {
  assert.equal(parseCommit("feat(orders)!: drop v1 API")?.breaking, true);
});

test("globs are segment-aware", () => {
  assert.ok(globToRegExp("*.pem").test("key.pem"));
  assert.ok(!globToRegExp("*.pem").test("certs/key.pem"));
  assert.ok(globToRegExp("**/*.pem").test("certs/deep/key.pem"));
  assert.ok(matchesAny("api/.env.local", DEFAULT_POLICY.forbiddenFiles));
  assert.ok(matchesAny("api/.env.example", DEFAULT_POLICY.allowedFiles));
});

test("pushes to protected branches and badly named branches are blocked", () => {
  const sha = "a".repeat(40), zero = "0".repeat(40);
  const updates = parsePushUpdates(
    `refs/heads/main ${sha} refs/heads/main ${zero}\n` +
    `refs/heads/feat/12-pricing ${sha} refs/heads/feat/12-pricing ${zero}\n` +
    `refs/heads/wip ${sha} refs/heads/wip ${zero}\n` +
    `refs/tags/v1 ${sha} refs/tags/v1 ${zero}\n`);
  const problems = validatePush(updates, DEFAULT_POLICY);
  assert.equal(problems.length, 2);
  assert.match(problems[0], /directly to 'main'/);
  assert.match(problems[1], /'wip' doesn't match/);
});

test("defineHooks merges over defaults", () => {
  const p = defineHooks({ protectedBranches: ["trunk"], commit: { requireScope: true } });
  assert.deepEqual(p.protectedBranches, ["trunk"]);
  assert.equal(p.commit.requireScope, true);
  assert.equal(p.commit.maxHeaderLength, 72);
});
