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
