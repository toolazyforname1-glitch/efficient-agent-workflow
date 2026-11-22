# Efficient Agent Workflow — RulePack

This tool makes sure an agent batches its work: every known file write goes out in one message, independent tool calls and commands go out together, and long-running jobs are watched without wasting extra turns. It ships those rules as 15 named, independently selectable blocks, delivered either as AGENTS.md instructions (recommended) or as a skill, through a questionnaire that launches minimized and never steals your focus.

## Summary
PUBLISHED - 15 named, independently selectable rules and a questionnaire installer that launches in a minimized window. GitHub release `1.0.0` is live.

## What is inside

- `skill/SKILL.md` — the complete skill: YAML frontmatter plus all 15 rules under their own named headings.
- `skill/references/` — one file per named rule. These are the canonical rule texts, grouped by purpose:
  - File writes: `all-known-file-writes.md`, `mandatory-preflight.md`, `batching-examples.md`, `legitimate-serialisation.md`, `write-size-and-cost.md`
  - Command usage: `batch-independent-calls.md`, `all-tool-types.md`, `batch-examples-and-guardrails.md`, `writes-and-todowrite.md`, `dependency-only-serialisation.md`, `time-ordered-commands.md`, `no-redundant-status-checks.md`, `completion-conditions.md`, `detached-launch-pattern.md`, `sequential-rule.md`
- `install.bat` — double-clickable launcher. Finds a Python with Textual, checks the dependency (never auto-installs), then starts the TUI in a new minimized window.
- `installer/questionnaire.py` — the Textual wizard.
- `installer/test_smoke.py` — headless test, opens no window.
- `installer/requirements.txt` — `textual>=0.80`.

## Using the installer

Double-click `install.bat`, then restore the minimized window from the taskbar.

1. **Format** — `AGENTS.md instructions` is marked Recommended and preselected; `Skill (SKILL.md)` is the alternative. A detail panel explains the choice.
2. **Rules** — all 15 named rules are checked. Uncheck any to remove it; `Select all` / `Clear all` and the `a` / `n` shortcuts are there too. Focusing a rule shows its exact text in the right-hand preview pane.
3. **Delivery** — for AGENTS.md, choose paste-ready text (default, written to `output/agents-md-addendum.md`) or auto-append to a target file (default `~/AGENTS.md`, with validation and a payload preview). For Skill, a generated `SKILL.md` plus the selected reference files are written to `output/skill/`.
4. **Done** — summary of every selected rule and the destination, with copy-to-clipboard and open-output actions.

Exit with `q`, `Esc`, `Ctrl+C`, or by closing the window. The output folder is created on first run.

## Manual use

Copy the whole `skill/` folder into a skills directory, for example `~/.config/opencode/skills/efficient-agent-workflow/`. Keep `SKILL.md` at the root and `references/` beside it.

## Verification

- `python -m py_compile installer/questionnaire.py` passes.
- `python installer/test_smoke.py` passes headlessly: AGENTS.md recommended, all 15 rules checked, auto-install No.
- The TUI was visually checked with `probe.ps1` from the real ss tool while parked off-screen, so no window appeared and no input focus was taken.

## Windows standalone build

`install.exe` is a one-file build of the installer. Double-click it (or run it from a terminal); it relaunches itself with a minimized TUI window, exactly like `install.bat`. Rule text is bundled inside the exe, and output is written to an `output` folder next to the exe.

To rebuild it:

```
pyinstaller --onefile --clean --collect-all textual --add-data "skill\references;skill\references" --distpath dist installer\entry.py
```

Copy `dist\install.exe` next to `skill\` and `install.bat` if you want the source tree and the standalone build side by side.

## GitHub

Release `1.0.0` is published at https://github.com/toolazyforname1-glitch/efficient-agent-workflow/releases/tag/1.0.0 with `install.exe` attached. The source lives in the repository root; no credentials or secrets are included.

If this project saved you time, donations are welcome:

Bitcoin   bc1qv7f4v8djjw46wyhw0c8nfdufdy9mgnwcndvyyc
Solana    7uCSuGumHHAKLw8KAwEthhwJgGvFprjZs8pQ4c7vvNud
EVM       0x876Dbb0D860e813Ea57885B717fc860039Db7337
Tron      TCU9ruV2qAbdfPkby28WXNGwv7WDDexXsV
Ton       UQBmx9jzmKV6hhUF6mZ-2DIHKSBc8zwYtqAZZRL6UPAApFmx
