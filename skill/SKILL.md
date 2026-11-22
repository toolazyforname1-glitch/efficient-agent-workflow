---
name: efficient-agent-workflow
description: Named rules for batching file writes and reducing tool-call overhead. Use when writing several files, issuing independent tool calls, or watching long-running jobs.
---

# Efficient Agent Workflow

Fifteen named rules. Each is independent; apply the ones that fit the task.

## One message for every file write

# ⛔ BATCH FILE WRITES — ALL KNOWN FILES IN ONE MESSAGE (SET IN STONE, 2026-11-05)

**THE BUG THIS KILLS:** writing ONE file, ending the turn, waiting for the tool result, then spending a whole new request to write the NEXT file. Each `write`/`edit` call that sits alone in its turn costs a full extra request — entire context re-sent, full decode. 10 independent files written one-per-turn = **10 requests**. The same 10 written in one message = **1 request**.

**THE RULE:** if you already know the content of K files, emit ALL K `write` tool calls in the SAME assistant message, before any of their results come back. Never write file 1, "look at it", then think about file 2. Think once for all of them, plan all K contents, then emit K tool calls in one block. Independent files by definition do not need each other's results.

## Pre-flight before the first write

**MANDATORY PRE-FLIGHT — before the FIRST write of any multi-file task:**
1. Enumerate every file the task needs (write the list in your todos or inline).
2. For each one: decide the final path AND the full final content NOW.
3. Emit all `write` calls together in one message. Only then read results.

## Good and bad batching examples

**GOOD:**
- "Create 6 module files" → ONE message, 6 `write` calls.
- "Write 10 big files, no external info needed" → ONE message, 10 `write` calls.
- Mixed task → `write` ×N + `todowrite` + independent bash all in ONE message.

**BAD — the exact pattern to eliminate:**
- `write` file1 → end turn → result → `write` file2 → end turn → … (N requests)
- `write` one file, then a paragraph of narration, then the next file next turn.
- "I'll create the config first" logic when the config content was already known.

## When serialising is legitimate

**WHEN SERIALISING IS LEGITIMATE (only these cases):**
- File B's content genuinely depends on a value read from file A or from a command output (generated code, a version string, a test result).
- A SINGLE file too large for one `write` call — build it with successive `edit`/append calls. That is one file; it never justifies serialising OTHER independent files.
- A tool result is required before the next step (test output, build error, search hit).

## Write size and cost math

**SIZE INTERACTION:** the write-tool reliability rules (~2000–3000 chars per call, JSON escaping) apply PER CALL and still hold. Smaller calls are fine — they just all go in the SAME message. Batching many medium writes in one message is the default; splitting one oversized file across calls is the narrow exception.

**COST MATH:** 1 extra request = whole context re-sent + full decode. Batching 10 writes into one message removes 9 full requests. In any multi-file task this is the single largest saving available — bigger than any output trimming.

## Batch independent calls

- **BATCH independent tool calls in ONE message.** Never send commands one at a
  time when the second does not depend on the first's output — send them together.

## Every tool type, not just shell

- **This applies to ALL tool types, not just shell commands.** Anything
  independent — several `edit` calls, several `write` calls, multiple bash
  commands, a web search (EXA / Firecrawl / context7), a `todowrite` — can go in
  ONE message instead of one per turn. Every extra turn is a whole extra request
  against the model; batching is the single biggest token saving available, far
  larger than trimming output.

## Batch examples and guardrails

  - **Example** (illustrative ONLY — the shape of any given batch depends
    entirely on the task, and a batch of this size is not expected or required):
    suppose a test result tells you four files need fixing, two unrelated
    commands need running, and something needs looking up. Then that is one
    message, not seven turns. The principle is "batch what is independent"; the
    numbers are just an illustration of it.
  - **Do not invent work to fill a batch**, and do not hold back a dependent
    step to make a batch look bigger. Batching is a consequence of independence,
    never a target to hit.

## Write/edit and todo batching

  - **Multiple `write`/`edit` calls on DIFFERENT files are ALWAYS independent —
    emit all of them in ONE message.** Writing file 1, ending the turn, then
    writing file 2 in the next request is the most expensive habit in this
    harness: N files = N requests instead of 1. See "BATCH FILE WRITES" at the
    top of this file. (Payload-size rules still apply per call; they never
    justify serialising across turns.)
  - `todowrite` is independent of everything — batch it with the work it
    describes rather than spending a turn on it alone.

## Dependency is the only serialiser

- **Dependency is the ONLY reason to serialise.** If command B needs command A's
  output (a path, an ID, a value read from a file, a test result), then A alone
  first is correct. Judge by "does B literally need A's output to be written?",
  not by habit or by topic similarity.

## Time-ordered commands in one request

- **TIME-ordered commands belong in ONE request, not two.** If command B can only
  start after command A finishes but B does NOT need A's output (pure ordering, no
  data handoff), do NOT spend a whole extra request waiting for A: run BOTH in the
  same request using a **watchdog** — a detached watcher that polls A's completion
  condition (process gone, result file appeared, threshold reached) and then
  executes B — or a **simple estimate plus `Start-Sleep`** before B. Either way both
  commands really execute inside a single request, which saves the context re-send
  and the full decode of an extra turn.
  - Watchdog pattern: one detached script polls the condition internally, runs B when
    satisfied, writes one summary file, exits — no session-shell polling loop.
  - Estimate pattern: `Start-Sleep -Seconds <n>` between A and B in the same command
    when A's duration is predictable; both land in one request.
  - The rule is about *time* dependencies, not *data* dependencies: if B needs A's
    actual output, A must still run and report first.

## No redundant status checks

- **NEVER repeat a status/monitoring command "just to check".** If a long run
  needs watching, write ONE detached script that polls internally and exits
  itself on a completion condition; then read its single output file at natural
  checkpoints (user ping / todo continuation), at most ONE check per activation.

## Completion conditions to script

- **Completion conditions to script**: result file appears · target process gone
  · GPU util+VRAM dropped to idle (run ended) · timeout. The script writes one
  summary file and exits — no session-shell polling loops.

## Detached launch pattern

- **Launch pattern for long runs**: detached via WMI `Win32_Process Create`
  (crash-safe), capture PID once, hand monitoring to a watcher script
  (`%TEMP%\opencode\wait_probe.ps1 -Tag <tag>` → writes `<tag>_final.txt`).

## Sequential rule

- **Sequential rule**: only send the second command after the first when it truly
  depends on the first's result; otherwise run in parallel.
