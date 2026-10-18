// Git hook policy for this repository, as typed TypeScript. Lefthook runs the hooks; Plumbline's library
// (.plumbline/hooks/lib.mts) supplies the defaults and the types. Change this file through a reviewed PR.
//
//   Typecheck:  npx -p typescript -p @types/node tsc -p .plumbline/hooks
//   Unit tests: node --test .plumbline/hooks/lib.test.mts
import { defineHooks } from "./.plumbline/hooks/lib.mts";
import type { HookContext } from "./.plumbline/hooks/lib.mts";

export default defineHooks({
  protectedBranches: ["__DEFAULT_BRANCH__"],

  commit: {
    // Commit scopes must be modules from ARCHITECTURE.md (plus a few repo-wide scopes like deps, ci, docs).
    scopes: "architecture",
    requireScope: false,
    requireAiTrailer: __REQUIRE_TRAILER__,
  },

  // Programmatic checks: return a list of problems; an empty list passes.
  checks: {
    preCommit: [
      // Example: database migrations need a matching rollback file.
      (ctx: HookContext) =>
        ctx.stagedFiles
          .filter((f) => /migrations\/.*\.up\.sql$/.test(f))
          .filter((f) => !ctx.stagedFiles.includes(f.replace(/\.up\.sql$/, ".down.sql")))
          .map((f) => `'${f}' has no matching .down.sql rollback.`),
    ],
    prePush: [],
  },
});
