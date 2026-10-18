// Plumbline TypeScript git hooks — shared library.
// Runs with Node's built-in type stripping (Node >= 22.18 / 23.6 by default; 22.6+ with a flag) or tsx.
// Only erasable TypeScript syntax is used: no enums, namespaces or parameter properties.

import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

/** Everything a custom check can look at. Reads come from the git index, so they see exactly what will be committed. */
export interface HookContext {
  hook: "pre-commit" | "commit-msg" | "pre-push";
  root: string;
  branch: string;
  stagedFiles: string[];
  readStaged: (path: string) => string;
  architectureModules: string[];
}

/** A programmatic check: return problem messages (empty array = pass). */
export type Check = (ctx: HookContext) => string[] | Promise<string[]>;

export interface CommitPolicy {
  /** Conventional Commit types allowed in the header. */
  types: string[];
  /** "architecture" = scopes must be module names from ARCHITECTURE.md (plus extraScopes); "any"; or a fixed list. */
  scopes: "architecture" | "any" | string[];
  extraScopes: string[];
  requireScope: boolean;
  maxHeaderLength: number;
  /** Require the `AI-Assisted: yes | partial | no` trailer on every commit. */
  requireAiTrailer: boolean;
  aiTrailerValues: string[];
}

export interface HookPolicy {
  protectedBranches: string[];
  /** Feature branches must match this (the format `plumbline worktree new` creates). */
  branchPattern: RegExp;
  commit: CommitPolicy;
  /** Files that must never be committed (glob: `*` matches within a path segment, `**` across). */
  forbiddenFiles: string[];
  allowedFiles: string[];
  maxFileSizeKb: number;
  blockConflictMarkers: boolean;
  checks: { preCommit: Check[]; prePush: Check[] };
}

export type HookPolicyInput = Partial<Omit<HookPolicy, "commit" | "checks">> & {
  commit?: Partial<CommitPolicy>;
  checks?: Partial<HookPolicy["checks"]>;
};

export const DEFAULT_POLICY: HookPolicy = {
  protectedBranches: ["main", "master"],
  branchPattern: /^(feat|fix|chore|docs|refactor|perf|test|build|ci|spike|adr)\/(\d+-)?[a-z0-9][a-z0-9-]*$/,
  commit: {
    types: ["feat", "fix", "refactor", "perf", "test", "docs", "build", "ci", "chore", "revert"],
    scopes: "architecture",
    extraScopes: ["deps", "ci", "docs", "release", "repo", "architecture", "adr", "policy", "rules", "hooks"],
    requireScope: false,
    maxHeaderLength: 72,
    requireAiTrailer: true,
    aiTrailerValues: ["yes", "partial", "no"],
  },
  forbiddenFiles: [".env", ".env.*", "**/.env", "**/.env.*", "*.pem", "**/*.pem", "*.key", "**/*.key",
    "**/id_rsa", "**/id_ed25519", "*.pfx", "**/*.pfx", "*.p12", "**/*.p12"],
  allowedFiles: [".env.example", "**/.env.example", ".env.sample", "**/.env.sample"],
  maxFileSizeKb: 1024,
  blockConflictMarkers: true,
  checks: { preCommit: [], prePush: [] },
};

/** Typed helper for plumbline.hooks.mts — merges your settings over the defaults. */
export function defineHooks(input: HookPolicyInput): HookPolicy {
  return {
    ...DEFAULT_POLICY,
    ...input,
    commit: { ...DEFAULT_POLICY.commit, ...input.commit },
    checks: {
      preCommit: input.checks?.preCommit ?? [],
      prePush: input.checks?.prePush ?? [],
    },
  };
}

// ------------------------------------------------------------------ git helpers
export function git(args: string[], cwd?: string): string {
  try {
    return execFileSync("git", args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  } catch {
    return "";
  }
}

export function repoRoot(): string {
  return git(["rev-parse", "--show-toplevel"]) || process.cwd();
}

export function currentBranch(root: string): string {
  return git(["branch", "--show-current"], root);
}

export function hasCommits(root: string): boolean {
  return git(["rev-parse", "--verify", "-q", "HEAD"], root) !== "";
}

export function stagedFiles(root: string): string[] {
  const out = git(["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], root);
  return out.split("\0").filter(Boolean);
}

export function readStaged(root: string, path: string): string {
  return git(["show", `:${path}`], root);
}

export function stagedSizeBytes(root: string, path: string): number {
  return Number(git(["cat-file", "-s", `:${path}`], root)) || 0;
}

// ------------------------------------------------------------------ architecture + config
/** Module names from the ```toml plumbline-architecture``` block in ARCHITECTURE.md. */
export function architectureModules(root: string): string[] {
  const file = join(root, "ARCHITECTURE.md");
  if (!existsSync(file)) return [];
  const block = /```toml[ \t]+plumbline-architecture[ \t]*\n([\s\S]*?)```/.exec(readFileSync(file, "utf8"));
  if (!block) return [];
  return [...block[1].matchAll(/^\s*name\s*=\s*"([^"]+)"/gm)].map((m) => m[1]);
}

export async function loadPolicy(root: string): Promise<HookPolicy> {
  const file = join(root, "plumbline.hooks.mts");
  if (!existsSync(file)) return DEFAULT_POLICY;
  const mod: { default?: HookPolicy } = await import(pathToFileURL(file).href);
  return mod.default ?? DEFAULT_POLICY;
}

export function context(hook: HookContext["hook"], root: string): HookContext {
  return {
    hook,
    root,
    branch: currentBranch(root),
    stagedFiles: hook === "pre-commit" ? stagedFiles(root) : [],
    readStaged: (path: string) => readStaged(root, path),
    architectureModules: architectureModules(root),
  };
}

// ------------------------------------------------------------------ pure rules (unit-tested)
/** Segment-aware glob: `*` within one folder, `**` across folders. */
export function globToRegExp(glob: string): RegExp {
  let re = "";
  for (let i = 0; i < glob.length; i++) {
    const c = glob[i];
    if (glob.startsWith("**/", i)) { re += "(?:.*/)?"; i += 2; }
    else if (glob.startsWith("**", i)) { re += ".*"; i += 1; }
    else if (c === "*") re += "[^/]*";
    else if (c === "?") re += "[^/]";
    else re += c.replace(/[.+^${}()|[\]\\]/g, "\\$&");
  }
  return new RegExp(`^${re}$`);
}

export function matchesAny(path: string, globs: string[]): boolean {
  return globs.some((g) => globToRegExp(g).test(path));
}

export interface ParsedCommit {
  type: string;
  scope: string | undefined;
  breaking: boolean;
  subject: string;
  header: string;
  trailers: Record<string, string>;
}

/** Strip git comments and parse a Conventional Commit. Returns undefined when the header doesn't match. */
export function parseCommit(raw: string): ParsedCommit | undefined {
  const text = raw.split("\n").filter((l) => !l.startsWith("#")).join("\n").trim();
  const header = text.split("\n")[0] ?? "";
  const m = /^(?<type>[a-z]+)(?:\((?<scope>[^)]+)\))?(?<bang>!)?: (?<subject>\S.*)$/.exec(header);
  if (!m?.groups) return undefined;
  const paragraphs = text.split(/\n\s*\n/);
  const last = paragraphs.length > 1 ? paragraphs[paragraphs.length - 1] : "";
  const trailers: Record<string, string> = {};
  for (const line of last.split("\n")) {
    const t = /^([A-Za-z][A-Za-z-]*):\s*(.+)$/.exec(line.trim());
    if (t) trailers[t[1]] = t[2].trim();
  }
  return {
    type: m.groups.type,
    scope: m.groups.scope,
    breaking: Boolean(m.groups.bang) || /^BREAKING[ -]CHANGE:/m.test(text),
    subject: m.groups.subject,
    header,
    trailers,
  };
}

export function isExemptCommit(raw: string): boolean {
  return /^(Merge |Revert "|fixup! |squash! |amend! )/.test(raw.trimStart());
}

export function validateCommit(raw: string, policy: CommitPolicy, modules: string[]): string[] {
  if (isExemptCommit(raw)) return [];
  const c = parseCommit(raw);
  if (!c) {
    return ["Header must be a Conventional Commit: `type(scope): subject` — e.g. `feat(orders): reject zero quantity`."];
  }
  const problems: string[] = [];
  if (!policy.types.includes(c.type)) {
    problems.push(`Type '${c.type}' isn't allowed. Use one of: ${policy.types.join(", ")}.`);
  }
  const allowedScopes =
    policy.scopes === "any" ? undefined
    : policy.scopes === "architecture" ? (modules.length ? [...modules, ...policy.extraScopes] : undefined)
    : [...policy.scopes, ...policy.extraScopes];
  if (c.scope === undefined && policy.requireScope) {
    problems.push(`A scope is required${allowedScopes ? `: one of ${allowedScopes.join(", ")}` : ""}.`);
  }
  if (c.scope !== undefined && allowedScopes) {
    for (const s of c.scope.split(",").map((x) => x.trim())) {
      if (!allowedScopes.includes(s)) {
        problems.push(`Scope '${s}' isn't a module in ARCHITECTURE.md. Use one of: ${allowedScopes.join(", ")}.`);
      }
    }
  }
  if (c.header.length > policy.maxHeaderLength) {
    problems.push(`Header is ${c.header.length} characters; keep it to ${policy.maxHeaderLength}.`);
  }
  if (c.subject.endsWith(".")) problems.push("Subject shouldn't end with a full stop.");
  if (policy.requireAiTrailer) {
    const v = c.trailers["AI-Assisted"]?.toLowerCase();
    if (!v) {
      problems.push(`Add the provenance trailer as the last paragraph, e.g.\n\n    AI-Assisted: yes\n    AI-Tool: claude-code`);
    } else if (!policy.aiTrailerValues.includes(v)) {
      problems.push(`AI-Assisted must be one of: ${policy.aiTrailerValues.join(", ")}.`);
    }
  }
  return problems;
}

export interface PushUpdate {
  localRef: string;
  localSha: string;
  remoteRef: string;
  remoteSha: string;
}

const ZERO = /^0+$/;

/** Parse the lines git writes to a pre-push hook's stdin. */
export function parsePushUpdates(stdin: string): PushUpdate[] {
  return stdin.split("\n").map((l) => l.trim().split(/\s+/)).filter((p) => p.length === 4)
    .map(([localRef, localSha, remoteRef, remoteSha]) => ({ localRef, localSha, remoteRef, remoteSha }));
}

export function validatePush(updates: PushUpdate[], policy: HookPolicy): string[] {
  const problems: string[] = [];
  for (const u of updates) {
    const branch = u.remoteRef.replace(/^refs\/heads\//, "");
    if (!u.remoteRef.startsWith("refs/heads/")) continue;
    if (policy.protectedBranches.includes(branch)) {
      problems.push(ZERO.test(u.localSha)
        ? `Deleting '${branch}' is not allowed.`
        : `Pushing directly to '${branch}' is not allowed. Push a feature branch and open a pull request for human review.`);
    } else if (!ZERO.test(u.localSha) && !policy.branchPattern.test(branch)) {
      problems.push(`Branch '${branch}' doesn't match ${policy.branchPattern}. ` +
        "Create branches with `plumbline worktree new <issue>` (e.g. feat/123-short-title).");
    }
  }
  return problems;
}

export function report(hook: string, problems: string[]): void {
  if (!problems.length) return;
  process.stderr.write(`\nPlumbline ${hook} hook found ${problems.length} problem(s):\n\n`);
  for (const p of problems) process.stderr.write(`  ✗ ${p.replace(/\n/g, "\n    ")}\n`);
  process.stderr.write("\n");
  process.exitCode = 1;
}
