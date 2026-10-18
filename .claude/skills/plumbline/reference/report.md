# /plumbline report [--since 30d]

1. `plumbline check --all --format json`.
2. Append to `.plumbline/history.jsonl`:
   `{"ts", "commit": <git rev-parse --short HEAD>, "score", "errors", "warns", "infos", "by_rule": {...}, "files_scanned"}`
3. AI-provenance mix in the window:
   `git log --since=<window> --format='%(trailers:key=AI-Assisted,valueonly)'` → counts of yes / partial / no / missing.
4. Summarise for an engineering lead: current score vs earliest snapshot in the window; top 3 rule hotspots and the
   files driving them; architecture health (PL013/PL017 counts by module); provenance compliance; baseline debt
   remaining; one recommended action for next sprint.
5. With 3+ snapshots, show the score trend as a small chart.
