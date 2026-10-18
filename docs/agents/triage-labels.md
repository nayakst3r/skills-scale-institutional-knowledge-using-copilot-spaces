# Triage labels

| Role | Label | Who applies it |
|---|---|---|
| New, not yet looked at | `needs-triage` | anyone |
| Spec or tickets drafted by an agent, waiting for sign-off | `needs-human-approval` | agents |
| Approved and safe for an agent to pick up | `ready-for-agent` | **humans only** — the Plumbline guard blocks agents applying it |
| Needs a person (judgement, access, or a decision) | `ready-for-human` | anyone |
| Won't be done | `wontfix` | humans |
| Architecture module the work belongs to | `module:<name>` | anyone; must match `ARCHITECTURE.md` |

To rename the agent-ready label, change `agent_ready_label` in `plumbline.toml` and here, together.
