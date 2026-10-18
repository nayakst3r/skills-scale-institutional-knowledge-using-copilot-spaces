# /plumbline new <name> <python|node|dotnet> [github|azure|gitlab]

Create a greenfield project with guardrails from the first commit. If name or stack is missing, ask once.

1. Create `<name>/`, refuse if it exists and is non-empty, then `git init -b main` inside it.
2. Run `plumbline init --target <name> --ci <ci or auto>`.
3. Run the `architecture create` flow (`architecture.md`) — module paths must match the skeleton you will write,
   e.g. `src/<pkg>/domain/**`.
4. Write a **minimal, working** skeleton inside the declared modules. Every file must run; no placeholders:
   - **python**: `pyproject.toml` (`requires-python >= 3.11`, `pytest` in a `dev` dependency group), `src/<pkg>/__init__.py`,
     one small real function in the domain module, `tests/test_<x>.py` testing it.
   - **node**: `package.json` (`"type": "module"`, `"test": "node --test"`), one small real function in the domain
     module, `test/<x>.test.js`.
   - **dotnet**: `dotnet new sln`, classlib + xunit projects (requires the `dotnet` CLI; stop and say so if missing).
   Set the `test` target in the `Makefile` to the stack's runner. Add a stack `.gitignore`.
5. Add a CI test job with the `ci add test` flow (`ci.md`).
6. Run `make test` and `plumbline check --all`. Both must pass; fix anything that doesn't.
7. First commit: `chore: bootstrap <name> with Plumbline` with `AI-Assisted: yes` and `AI-Tool:` trailers.
8. Report the tree (depth 2), test result, gate score, and what is left: push, add `ANTHROPIC_API_KEY`,
   `/plumbline protect`.
