# AI Usage Policy

Applies to everyone contributing to this repository. Organisation-wide policy takes precedence where stricter.

## 1. Accountability
The engineer who opens a pull request owns every line in it, regardless of how it was produced. "The AI wrote it"
does not transfer responsibility for defects, security issues or licence problems.

## 2. Approved tools
| Tool | Approved use | Notes |
|---|---|---|
| Claude Code (organisation account) | All development tasks | Enterprise data controls apply |
| Other assistants | Only if listed by your organisation's approved-tools register | Personal or free-tier accounts are not approved for client work |

Agents run with the repository's configured hooks enabled. Disabling them is not permitted.

## 3. Data handling
| Data class | May be shared with an approved AI tool? |
|---|---|
| Public / open-source code | Yes |
| Internal source code in this repository | Yes, via approved tools |
| Secrets, credentials, keys, tokens | **Never** |
| Personal information (customer, employee) | **Never**, including in test fixtures — use synthetic data |
| Client-confidential documents not in this repo | Only with the engagement lead's written approval |

## 4. Disclosure and provenance
- Every PR completes the AI disclosure section of the PR template.
- Every commit carries an `AI-Assisted: yes | partial | no` trailer (enforced when `require_ai_trailer = true`).
- AI-generated architecture changes, security-sensitive code (auth, crypto, payments, access control) and data
  migrations require review by a code owner who did not use AI on that change.

## 5. Intellectual property and licensing
- Do not ask tools to reproduce third-party code, documentation or proprietary material.
- If generated code closely resembles a known open-source project, treat it as that project's code: check the licence
  and attribute or rewrite.
- New dependencies must have a licence on the organisation's allowed list.

## 6. Quality bar
AI-assisted work meets the same bar as any other work, enforced by the Plumbline gate, the AI architecture review and
human code review. See `AGENTS.md` for the definition of done.

## 7. Prohibited
- Generating or committing credentials, malware, or code designed to evade security controls.
- Using AI to bypass review: splitting changes to dodge thresholds, self-approving, or auto-merging.
- Representing AI-generated content as independently verified when it was not.

## 8. Incidents
Report a suspected leak of secrets or confidential data to an AI tool immediately via `SECURITY.md`. Rotate any
exposed credential; deleting it from the code is not enough.
