# ⛔ BATCH FILE WRITES — ALL KNOWN FILES IN ONE MESSAGE (SET IN STONE, 2026-11-05)

**THE BUG THIS KILLS:** writing ONE file, ending the turn, waiting for the tool result, then spending a whole new request to write the NEXT file. Each `write`/`edit` call that sits alone in its turn costs a full extra request — entire context re-sent, full decode. 10 independent files written one-per-turn = **10 requests**. The same 10 written in one message = **1 request**.

**THE RULE:** if you already know the content of K files, emit ALL K `write` tool calls in the SAME assistant message, before any of their results come back. Never write file 1, "look at it", then think about file 2. Think once for all of them, plan all K contents, then emit K tool calls in one block. Independent files by definition do not need each other's results.
