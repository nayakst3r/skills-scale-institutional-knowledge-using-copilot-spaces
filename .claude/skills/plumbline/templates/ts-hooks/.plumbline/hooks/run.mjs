// Launcher for Plumbline's TypeScript hooks. Plain JavaScript so it runs on any Node version, then picks the best
// way to execute TypeScript: built-in type stripping (Node >= 22.18 / 23.6), the flag (22.6+), or `npx tsx`.
//   node .plumbline/hooks/run.mjs <pre-commit|commit-msg|pre-push> [git hook args...]
//   node .plumbline/hooks/run.mjs --check     prints which runtime will be used
import { spawnSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const [, , hook, ...args] = process.argv;
const [major, minor] = process.versions.node.split(".").map(Number);
const native = Boolean(process.features?.typescript);
const flag = !native && (major > 22 || (major === 22 && minor >= 6));
const mode = native ? "native" : flag ? "flag" : "tsx";

if (hook === "--check") {
  console.log(`node ${process.versions.node}: ${mode === "native" ? "built-in type stripping"
    : mode === "flag" ? "type stripping via --experimental-strip-types" : "npx tsx (upgrade to Node >= 22.18 to drop it)"}`);
  process.exit(0);
}
if (!["pre-commit", "commit-msg", "pre-push"].includes(hook)) {
  console.error(`run.mjs: unknown hook '${hook ?? ""}'`);
  process.exit(2);
}
const file = join(here, `${hook}.mts`);
if (native) {
  process.argv = [process.argv[0], file, ...args];
  await import(pathToFileURL(file).href);
} else {
  const cmd = flag ? process.execPath : "npx";
  const cmdArgs = flag ? ["--experimental-strip-types", "--no-warnings", file, ...args] : ["--yes", "tsx", file, ...args];
  const r = spawnSync(cmd, cmdArgs, { stdio: "inherit" });
  process.exit(r.status ?? 1);
}
