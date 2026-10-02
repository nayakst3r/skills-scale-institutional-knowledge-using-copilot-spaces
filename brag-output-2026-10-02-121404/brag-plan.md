# /brag plan (v2): AI-assisted engineering at scale. Deloitte Data & AI practice.

## The questions
- **What is it?** A best-practice operating model, with a sample framework repo, for keeping architecture and intent intact when a large practice builds with AI assistants.
- **Who is it for?** The Data & AI practice (~400 engineers), presented by the Chief AI Officer. Any team size, any of five data stacks.
- **The problem it solves:** AI makes every engineer faster, but at scale it also multiplies drift: reads across domain boundaries, in-place breaking schema changes, hard-coded environments, untested models. Docs can't keep up; reviewers can't see everything.
- **What sets it apart?** Intent is encoded where every engineer and every AI will meet it: context in the repo (`AGENTS.md`, Copilot instructions), principles as CI checks, ownership as CODEOWNERS, delivery through gated CI/CD.
- **Most convincing moment:** two real failures from the sample repo, `cross-domain-read` and `contract-compat`, blocking off-architecture changes before merge, then the correct fix passing.
- **Visual hook:** a main branch with AI-driven branches multiplying, several turning red with real rule names. "Speed goes up. So does drift."
- **Real UI shown:** verbatim output and file content from `data-platform-framework/` (see `work/real-output.txt`): `use-stack.sh`, `make check`, local build summary, `AGENTS.md` rules, the `ARCHITECTURE.md` "Enforced by" column, the ruleset's required checks, `CODEOWNERS`, the two violations, and the step-6 guardrail diff. PR check pills and the CI/CD pipeline are illustrative UI using the real check and stage names.
- **Tone:** `polished`. Executive, calm, confident. Step-by-step so a practice can follow it.
- **Format:** landscape 1920×1080, 30 fps, ~81 s (longer than a usual /brag because it is a step-by-step walkthrough).

## Brand
Deloitte digital look: black background, white type, Deloitte Green `#86BC25` as the single accent (also used for "pass"), dark green `#26890D`, red `#DA291C` for failures, cool grey `#A7A8AA` for secondary text. Typeface: Open Sans. Wordmark: "Deloitte" + green dot, recreated in type. Swap in the official logo file from the brand library before external use.

## Storyboard

| Time | Scene | Read line(s) |
|---|---|---|
| 0.0–10.0 | **The problem.** Branches multiply off `main`, each tagged AI; several turn red with real rule names | "Every engineer now codes with an AI assistant." / "Speed goes up. So does drift." / "So how do you keep the intent and the architecture intact at scale?" |
| 10.0–14.0 | **Title.** Deloitte wordmark | "Context as code. Principles as CI." / "A best-practice operating model for AI-assisted data engineering" |
| 14.0–34.0 | **Step 1: the first engineer sets the rules.** 1a start from the framework + pick the stack; 1b write the context every AI reads (`AGENTS.md`); 1c turn principles into checks; 1d protect `main` (ruleset + CODEOWNERS) | Step title + the four sub-step labels |
| 34.0–48.0 | **Step 2: many teams build in parallel.** Three PRs (Finance with Copilot agent mode, Sales with Copilot, an issue handled by the Copilot coding agent) run the same five required checks; Finance fails `principles`, fixes, passes; all three merge through the queue | "Every change, human or AI, passes the same gates." / "3 features merged. main stays green." |
| 48.0–58.0 | **Step 3: the gates catch drift.** Two real failures and their correct fixes | "The gates protect intent, not just syntax." |
| 58.0–66.0 | **Step 4: CI/CD promotes.** PR checks → merge queue → main → stg (Terraform + dbt build + tests) → release tag → prod (approval) | "Only CI deploys. People approve." |
| 66.0–73.0 | **Step 5: the practice learns.** Retro → ADR → `AGENTS.md` rule + new check → every engineer's AI knows it | "One PR updates every engineer's AI." |
| 73.0–81.0 | **Close.** Five stacks; Deloitte wordmark | "Any team size. Any of five stacks." / "The repo holds the intent. CI protects it." |

A step tracker along the bottom (1–5) keeps the walkthrough legible throughout.

## Sound
120 bpm, A minor, music and effects as one piece. Sparse, tense pulse under the problem; the groove lands on the title; steady through the steps; a breakdown for "the practice learns"; resolve on the close. Effects in key and under the music: quiet ticks for typing, a soft low A for each failure, rising plucks for passing checks, a warm chord for each merge, ascending notes as pipeline stages light.
