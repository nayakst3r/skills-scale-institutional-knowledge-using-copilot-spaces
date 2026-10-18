// Plumbline commit-msg hook: Conventional Commits, scopes from ARCHITECTURE.md modules, AI provenance trailer.
import { readFileSync } from "node:fs";
import { architectureModules, loadPolicy, repoRoot, report, validateCommit } from "./lib.mts";

const file = process.argv[2];
if (!file) {
  process.stderr.write("commit-msg hook: missing message file argument\n");
  process.exit(2);
}
const root = repoRoot();
const policy = await loadPolicy(root);
report("commit-msg", validateCommit(readFileSync(file, "utf8"), policy.commit, architectureModules(root)));
