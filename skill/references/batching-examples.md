**GOOD:**
- "Create 6 module files" → ONE message, 6 `write` calls.
- "Write 10 big files, no external info needed" → ONE message, 10 `write` calls.
- Mixed task → `write` ×N + `todowrite` + independent bash all in ONE message.

**BAD — the exact pattern to eliminate:**
- `write` file1 → end turn → result → `write` file2 → end turn → … (N requests)
- `write` one file, then a paragraph of narration, then the next file next turn.
- "I'll create the config first" logic when the config content was already known.
