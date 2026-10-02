# /brag plan: data-platform-framework

## The questions
- **What is it?** A repo template and working method that lets ~10 data engineers, each with an AI assistant, build one data platform without breaking the architecture, on any of five stacks.
- **Who is it for?** Data engineering leads and teams standardizing on VS Code + GitHub Copilot.
- **What sets it apart?** The architecture isn't a document; it runs in CI. Context lives in the repo (`AGENTS.md`), so every Copilot session starts with the same rules. One method covers Fabric/Azure, Databricks, Snowflake, GCP, and AWS.
- **Most impressive claim (true, and tested):** when Copilot writes off-architecture SQL, `make check` blocks it with the exact rule; the same tests pass on all five stacks.
- **Visual hook:** ten editor tiles, each "engineer + Copilot" typing a different line at once (chaos), collapsing into one line: *One architecture.*
- **Real UI to show:** the framework's own terminal output, captured verbatim (`work/real-output.txt`): `use-stack.sh`, the `cross-domain-read` failure, the `contract-compat` failure, and the five green stacks from `verify-all-stacks.sh`. Code lines are from the repo's real dbt models.
- **Tone:** `polished` with a little punch: serious, restrained, a client-ready practice demo. Hard truths delivered calmly.
- **Share caption:** see `share-copy.txt`.

## Visual identity
- Background: deep ink `#0B0F14`; panels `#111820`, hairlines `#223040`.
- The project's own metaphor as the accent system, the medallion layers: bronze `#C07A45`, silver `#B9C3CF`, gold `#E6B450`.
- Status colors from the terminal: pass `#3FB950`, fail `#F85149`.
- Type: Inter (headings, captions), JetBrains Mono (code, terminal).

## Storyboard (22.0 s, 120 bpm, cuts on the beat)

| # | Time | Scene | On screen | Read line (held ≥ 0.3 s/word) |
|---|---|---|---|---|
| 1 | 0.0–3.0 | Hook | 5×2 grid of editor tiles, each "engineer NN · Copilot" typing a different real line; slight jitter | "10 engineers. 10 AI assistants." |
| 2 | 3.0–6.5 | Reveal | Tiles collapse into one; medallion bar draws bronze → silver → gold; chips `AGENTS.md` `ARCHITECTURE.md` `CODEOWNERS` | "One architecture." / "Context in the repo. Principles in CI." |
| 3 | 6.5–10.5 | Highlight: any stack | Terminal: `./scripts/use-stack.sh` lists 5 stacks; selector lands on databricks; "Stack set to: Databricks…" | "Pick any of five stacks." |
| 4 | 10.5–14.5 | Highlight: guardrail | Copilot ghost text `from {{ ref('sales_silver_orders') }}`, then `make check` → red `[cross-domain-read] … only other domains' gold is allowed` / `FAIL: 1` | "Copilot goes off-architecture. CI says no." |
| 5 | 14.5–18.0 | Highlight: contracts | Contract diff `- amount` `+ gross_amount` → red `[contract-compat] … Create orders_v2.yaml instead (P5)` | "Breaking changes get blocked." |
| 6 | 18.0–22.0 | Punchline / outro | Five stacks tick green (`dbt parse: OK · local build: OK`), then end card | "One method. Five stacks." / "VS Code + GitHub Copilot · dbt · Terraform" |

Transitions: old content out, then new content in (no muddy crossfades); dip through the background between terminal scenes.

## Sound
120 bpm in A minor (Am – F – C – G, one chord per bar). Soft pad and pluck arpeggio from the start; kick and bass enter on the reveal (3.0 s); off-beat hats from 6.5 s. Effects in key, mixed under the music: quiet key ticks while typing, a low muted A thud under the red failures, a soft rising A-minor pluck for each green stack, a gentle swell into the end card and a ringing final chord.
