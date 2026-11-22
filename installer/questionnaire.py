"""RulePack Installer - Textual questionnaire for the efficient-agent-workflow pack."""
from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from rich.markup import escape
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Focus
from textual.widgets import Button, Checkbox, Footer, Input, RadioButton, RadioSet, Static

FROZEN = bool(getattr(sys, "frozen", False))
ROOT = Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parent.parent
REF_DIR = (Path(sys._MEIPASS) / "skill" / "references") if FROZEN else (ROOT / "skill" / "references")
OUTPUT_DIR = ROOT / "output"
SKILL_DIR = OUTPUT_DIR / "skill"


@dataclass(frozen=True)
class Rule:
    key: str
    name: str
    group: str
    hint: str
    filename: str


RULES: tuple[Rule, ...] = (
    Rule("write-all", "One message for every file write", "writes", "Emit all known writes before reading any result.", "all-known-file-writes.md"),
    Rule("preflight", "Pre-flight before the first write", "writes", "Enumerate files, decide content, then write in one block.", "mandatory-preflight.md"),
    Rule("examples", "Good and bad batching examples", "writes", "Concrete good and bad write-batching patterns.", "batching-examples.md"),
    Rule("serialise", "When serialising is legitimate", "writes", "The only three cases that justify sequential writes.", "legitimate-serialisation.md"),
    Rule("cost", "Write size and cost math", "writes", "Payload limits per call and the cost of extra turns.", "write-size-and-cost.md"),
    Rule("calls", "Batch independent calls", "commands", "Never serialise commands with no output dependency.", "batch-independent-calls.md"),
    Rule("tool-types", "Every tool type, not just shell", "commands", "edit, write, searches and todos batch too.", "all-tool-types.md"),
    Rule("guardrails", "Batch examples and guardrails", "commands", "Illustrative example and the do-not-invent rule.", "batch-examples-and-guardrails.md"),
    Rule("mixed", "Write/edit and todo batching", "commands", "Different files are always independent; batch todos.", "writes-and-todowrite.md"),
    Rule("dependency", "Dependency is the only serialiser", "commands", "Serialise only when B literally needs A's output.", "dependency-only-serialisation.md"),
    Rule("timing", "Time-ordered commands in one request", "commands", "Watchdog or estimate instead of a second turn.", "time-ordered-commands.md"),
    Rule("monitoring", "No redundant status checks", "commands", "One detached watcher, one summary file, one check.", "no-redundant-status-checks.md"),
    Rule("conditions", "Completion conditions to script", "commands", "File appears, process exits, GPU idles, or timeout.", "completion-conditions.md"),
    Rule("launch", "Detached launch pattern", "commands", "WMI Create, capture PID, hand off to a watcher.", "detached-launch-pattern.md"),
    Rule("sequential", "Sequential rule", "commands", "Only serialise on a true data dependency.", "sequential-rule.md"),
)

FORMAT_AGENTS = "agents"
FORMAT_SKILL = "skill"
STEPS = ("format", "rules", "deliver")


class QuestionnaireApp(App[None]):
    """Three-step wizard: format, rule selection, delivery."""

    TITLE = "RulePack Installer"

    CSS = """
    $accent: #ffb000;
    $text-success: #ffb000;
    $block-cursor-background: #ffb000;
    $block-cursor-foreground: #1a1a1a;
    Screen { background: #1a1a1a; color: #ededed; }
    #topbar {
        height: 3; background: #232323; border-bottom: solid #3a3a3a;
        padding: 0 2; content-align: left middle;
    }
    #topbar-name { color: #ffb000; text-style: bold; }
    #topbar-step { color: #56d4dd; }
    #body { height: 1fr; }
    #sidebar {
        width: 28; background: #202020; border-right: solid #363636;
        padding: 1 1; height: 100%;
    }
    #brand { color: #ffb000; text-style: bold; margin-bottom: 0; }
    #brand-sub { color: #8d8d8d; margin-bottom: 2; }
    .nav-item {
        color: #8d8d8d; padding: 1 1; margin-bottom: 1;
        border-left: wide transparent; background: #232323;
    }
    .nav-item.active {
        color: #ffffff; background: #3a3224; border-left: wide #ffb000;
        text-style: bold;
    }
    #side-hint { color: #7d7d7d; margin-top: 3; }
    #main { width: 1fr; padding: 1 2; height: 100%; }
    #step-head { color: #ffffff; text-style: bold; margin-bottom: 1; }
    .pane { display: none; height: 1fr; }
    .pane.active { display: block; }
    .pane-title { color: #ffb000; text-style: bold; margin-bottom: 1; }
    .hint { color: #a3a3a3; margin-bottom: 1; }
    .field-label { color: #d6d6d6; text-style: bold; margin: 1 0; }
    .error { color: #ff7070; }
    .ok { color: #6fdc9a; }
    RadioSet {
        background: #242424; border: round #3c3c3c;
        padding: 1 1; margin-bottom: 1; height: auto;
    }
    RadioButton { background: #242424; color: #ededed; padding: 1 2; height: auto; }
    RadioSet RadioButton:focus { background: #332d22; color: #ffcc55; }
    RadioSet RadioButton.-selected { background: #2f2a20; color: #ffcc55; }
    RadioSet RadioButton.-selected:focus { background: #3a3224; color: #ffd979; }
    RadioButton:focus > .toggle--label { background: #ffb000; color: #1a1a1a; text-style: bold; }
    RadioButton.-on > .toggle--button { color: #ffb000; }
    RadioSet RadioButton.-on > .toggle--label { background: #3a3224; color: #ffd979; }
    Checkbox > .toggle--button { background: #333333 !important; }
    Checkbox.-on > .toggle--button { background: #3a3224 !important; color: #ffb000 !important; }
    #fmt-detail {
        background: #222222; border: round #3c3c3c;
        padding: 1 2; color: #c8c8c8; height: auto;
    }
    #rules-layout { height: 1fr; }
    #rules-left { width: 58%; padding-right: 1; }
    #rules-right { width: 1fr; padding-left: 1; }
    #rules-scroll { height: 1fr; border: round #3c3c3c; background: #1f1f1f; }
    #rule-count { color: #56d4dd; margin-bottom: 1; }
    .rule-card {
        background: #252525; border: round #3c3c3c;
        padding: 0 1; margin-bottom: 1; height: auto;
    }
    .rule-card.writes { border-left: wide #ffb000; }
    .rule-card.commands { border-left: wide #56d4dd; }
    .rule-hint { color: #9e9e9e; margin-left: 3; padding-bottom: 1; }
    Checkbox { background: #252525; color: #ededed; }
    Checkbox:focus { background: #353535; color: #ffb000; }
    .rule-tools { height: auto; margin-bottom: 1; }
    #preview-label { color: #ffb000; text-style: bold; margin-bottom: 1; }
    #preview-scroll { height: 1fr; border: round #3c3c3c; background: #141414; padding: 0 1; }
    #preview-text { color: #d2d2d2; }
    Input { background: #141414; color: #ededed; border: solid #4a4a4a; }
    Input:focus { border: solid #ffb000; }
    #target-group { margin: 1 0; }
    #payload-box {
        height: 10; background: #141414; border: round #3c3c3c;
        padding: 0 1; color: #a8a8a8;
    }
    .nav { height: auto; margin-top: 1; }
    Button.accent { background: #8a6300; border: solid #ffb000; color: #fff6df; }
    Button.accent:focus { background: #a67800; border: solid #ffd166; color: #ffffff; }
    .path { color: #56d4dd; margin-bottom: 1; }
    #done-mark { color: #6fdc9a; text-style: bold; }
    Footer { background: #202020; color: #9a9a9a; }
    """

    BINDINGS = [
        Binding("q", "quit_app", "Quit"),
        Binding("escape", "quit_app", "Quit", priority=True),
        Binding("ctrl+c", "quit_app", "Quit", priority=True),
        Binding("enter", "next", "Next", priority=True),
        Binding("backspace", "back", "Back"),
        Binding("a", "select_all", "All"),
        Binding("n", "select_none", "None"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._step: str = STEPS[0]
        self._format: str = FORMAT_AGENTS
        self._auto: bool = False
        self._selected: set[str] = {rule.key for rule in RULES}
        self._blocks: dict[str, str] = {}
        self._preview_key: str | None = None
        self._message: str = ""
        self._nav_lock: bool = False

    def compose(self) -> ComposeResult:
        with Vertical(id="topbar"):
            yield Static(
                "[b]# RULEPACK INSTALLER[/]   [dim]|[/]   15 named rules   [dim]|[/]   "
                "[b]q[/] quit  [b]enter[/] next  [b]bksp[/] back",
                id="topbar-static",
            )
        with Horizontal(id="body"):
            with Vertical(id="sidebar"):
                yield Static("EFFICIENT", id="brand")
                yield Static("AGENT WORKFLOW", id="brand-sub")
                yield Static("01   FORMAT", classes="nav-item active", id="nav-format")
                yield Static("02   RULES", classes="nav-item", id="nav-rules")
                yield Static("03   DELIVER", classes="nav-item", id="nav-deliver")
                yield Static("enter  continue\nbksp   back\nq      quit", id="side-hint")
            with Vertical(id="main"):
                yield Static("", id="step-head")
                with Vertical(id="pane-format", classes="pane active"):
                    yield Static("Choose an output format", classes="pane-title")
                    yield Static("Both formats carry the same named rules. Pick how you want them delivered.", classes="hint")
                    with RadioSet(id="fmt"):
                        yield RadioButton("AGENTS.md instructions   (Recommended)", id="fmt-agents", value=True)
                        yield RadioButton("Skill   (SKILL.md with frontmatter)", id="fmt-skill")
                    yield Static("", id="fmt-detail")
                    with Horizontal(classes="nav"):
                        yield Button("Continue  >", id="next-format", variant="primary", classes="accent")
                with Vertical(id="pane-rules", classes="pane"):
                    yield Static("Pick the rules to include", classes="pane-title")
                    with Horizontal(id="rules-layout"):
                        with Vertical(id="rules-left"):
                            yield Static("", id="rule-count")
                            with Horizontal(classes="rule-tools"):
                                yield Button("Select all", id="select-all")
                                yield Button("Clear all", id="clear-all")
                            with VerticalScroll(id="rules-scroll"):
                                for rule in RULES:
                                    with Vertical(classes=f"rule-card {rule.group}"):
                                        yield Checkbox(rule.name, value=True, id=f"rule-{rule.key}")
                                        yield Static(rule.hint, classes="rule-hint")
                        with Vertical(id="rules-right"):
                            yield Static("RULE TEXT", id="preview-label")
                            with VerticalScroll(id="preview-scroll"):
                                yield Static("", id="preview-text")
                    with Horizontal(classes="nav"):
                        yield Button("< Back", id="back-rules")
                        yield Button("Continue  >", id="next-rules", variant="primary", classes="accent")
                with Vertical(id="pane-deliver", classes="pane"):
                    yield Static("Delivery", classes="pane-title")
                    with Vertical(id="deliver-agents"):
                        yield Static("Install automatically?", classes="field-label")
                        with RadioSet(id="auto"):
                            yield RadioButton("No  -  write paste-ready text", id="auto-no", value=True)
                            yield RadioButton("Yes  -  append to a file", id="auto-yes")
                        with Vertical(id="target-group"):
                            yield Static("Target file:", classes="field-label")
                            yield Input("~/AGENTS.md", id="target", placeholder="~/AGENTS.md")
                            yield Static("", id="target-error", classes="error")
                        yield Static("PAYLOAD PREVIEW", classes="field-label")
                        yield Static("", id="payload-box")
                    with Vertical(id="deliver-skill"):
                        yield Static("Generated skill:", classes="field-label")
                        yield Static(str(SKILL_DIR / "SKILL.md"), classes="path")
                        yield Static("Selected rule text and reference files are written here.", classes="hint")
                    with Horizontal(classes="nav"):
                        yield Button("< Back", id="back-deliver")
                        yield Button("Finish", id="finish", variant="primary", classes="accent")
                with Vertical(id="pane-done", classes="pane"):
                    yield Static("[b]COMPLETE[/]", id="done-mark")
                    yield Static("", id="done-summary")
                    yield Static("", id="done-status", classes="ok")
                    with Horizontal(classes="nav"):
                        yield Button("Copy to clipboard", id="btn-copy")
                        yield Button("Open output", id="btn-open")
                        yield Button("Quit", id="btn-quit", variant="primary", classes="accent")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#target-group", Vertical).display = False
        self.query_one("#deliver-skill", Vertical).display = False
        self._set_step(STEPS[0])
        self._update_format_detail()
        self._update_count()
        self._show_preview(RULES[0].key)
        self.run_worker(self._load_rules, thread=True, exclusive=True)

    @work(thread=True)
    def _load_rules(self) -> None:
        blocks: dict[str, str] = {}
        missing: list[str] = []
        for rule in RULES:
            try:
                blocks[rule.key] = (REF_DIR / rule.filename).read_text(encoding="utf-8")
            except OSError:
                missing.append(rule.filename)
        self.call_from_thread(self._on_rules_loaded, blocks, missing)

    def _on_rules_loaded(self, blocks: dict[str, str], missing: list[str]) -> None:
        self._blocks = blocks
        self._show_preview(self._preview_key or RULES[0].key)
        self._update_payload()
        if missing:
            self._message = "Missing rule files: " + ", ".join(missing)
            self.notify(self._message, severity="error", timeout=10)

    def _set_step(self, step: str) -> None:
        self._step = step
        titles = {
            "format": "01  /  OUTPUT FORMAT",
            "rules": "02  /  RULE SELECTION",
            "deliver": "03  /  DELIVERY",
            "done": "DONE  /  SUMMARY",
        }
        self.query_one("#step-head", Static).update(titles.get(step, ""))
        active_nav = "deliver" if step == "done" else step
        for name in ("format", "rules", "deliver"):
            self.query_one(f"#nav-{name}", Static).set_class(name == active_nav, "active")
        for name in ("pane-format", "pane-rules", "pane-deliver", "pane-done"):
            active = name == f"pane-{step}"
            self.query_one(f"#{name}", Vertical).set_class(active, "active")

    def _update_format_detail(self) -> None:
        detail = self.query_one("#fmt-detail", Static)
        if self._format == FORMAT_AGENTS:
            detail.update(
                "[b]AGENTS.md instructions[/]\n"
                "Plain Markdown blocks made to paste into an AGENTS.md file. "
                "Choose paste-ready text or let the installer append it for you."
            )
        else:
            detail.update(
                "[b]Skill (SKILL.md)[/]\n"
                "A self-contained skill folder with YAML frontmatter and the selected "
                "rule text inlined under named headings."
            )

    def _update_count(self) -> None:
        chosen = len(self._selected)
        self.query_one("#rule-count", Static).update(
            f"SELECTED   [b]{chosen:02d}[/] / {len(RULES):02d}   [dim](space toggles, a/n all or none)[/]"
        )

    def _show_preview(self, key: str | None) -> None:
        if key is None:
            return
        self._preview_key = key
        rule = next((r for r in RULES if r.key == key), None)
        if rule is None:
            return
        body = self._blocks.get(key, "Loading rule text ...")
        header = f"[b]{escape(rule.name)}[/]   [dim]{rule.group}[/]\n\n"
        self.query_one("#preview-text", Static).update(header + escape(body))

    def _payload(self) -> str:
        blocks = [
            self._blocks[r.key].rstrip("\n")
            for r in RULES
            if r.key in self._selected and r.key in self._blocks
        ]
        return "\n" + "\n\n".join(blocks) + "\n"

    def _update_payload(self) -> None:
        payload = self._payload().strip()
        preview = payload[:320] + (" ..." if len(payload) > 320 else "")
        self.query_one("#payload-box", Static).update(escape(preview))

    def _target_path(self) -> Path:
        raw = self.query_one("#target", Input).value.strip() or "~/AGENTS.md"
        return Path(raw).expanduser()

    def _target_ok(self) -> bool:
        err = self.query_one("#target-error", Static)
        path = self._target_path()
        if path.name.upper() != "AGENTS.MD":
            err.update("Target must be a file named AGENTS.md.")
            return False
        if path.exists() and path.is_dir():
            err.update("Target path is a directory, not a file.")
            return False
        err.update("")
        return True

    def action_next(self) -> None:
        if self._nav_lock:
            return
        self._nav_lock = True
        self.set_timer(0.25, self._clear_nav_lock)
        if self._step == "format":
            self._set_step("rules")
        elif self._step == "rules":
            if not self._selected:
                self.notify("Select at least one rule.", severity="warning")
                return
            self._set_step("deliver")
            self._sync_delivery()
        elif self._step == "deliver":
            if self._format == FORMAT_AGENTS and self._auto and not self._target_ok():
                return
            self._finish()

    def action_back(self) -> None:
        if self._step == "rules":
            self._set_step("format")
        elif self._step == "deliver":
            self._set_step("rules")

    def action_select_all(self) -> None:
        if self._step != "rules":
            return
        self._selected = {rule.key for rule in RULES}
        for rule in RULES:
            self.query_one(f"#rule-{rule.key}", Checkbox).value = True
        self._update_count()

    def action_select_none(self) -> None:
        if self._step != "rules":
            return
        self._selected.clear()
        for rule in RULES:
            self.query_one(f"#rule-{rule.key}", Checkbox).value = False
        self._update_count()

    def action_quit_app(self) -> None:
        self.exit()

    def _clear_nav_lock(self) -> None:
        self._nav_lock = False

    def _sync_delivery(self) -> None:
        self.query_one("#deliver-agents", Vertical).display = self._format == FORMAT_AGENTS
        self.query_one("#deliver-skill", Vertical).display = self._format == FORMAT_SKILL
        self.query_one("#target-group", Vertical).display = self._auto and self._format == FORMAT_AGENTS
        self._update_payload()

    def _finish(self) -> None:
        self._set_step("done")
        chosen = [r.name for r in RULES if r.key in self._selected]
        if self._format == FORMAT_AGENTS:
            dest = str(self._target_path()) + " (append)" if self._auto else str(OUTPUT_DIR / "agents-md-addendum.md")
        else:
            dest = str(SKILL_DIR / "SKILL.md")
        self.query_one("#done-summary", Static).update(
            f"[b]Format[/]   {'AGENTS.md instructions' if self._format == FORMAT_AGENTS else 'Skill (SKILL.md)'}\n"
            f"[b]Rules[/]    {len(chosen)} of {len(RULES)}\n"
            f"[b]Output[/]  {escape(dest)}\n\n"
            + "\n".join(f"  - {escape(name)}" for name in chosen)
        )
        self.query_one("#done-status", Static).update("Working ...")
        if self._format == FORMAT_AGENTS and self._auto:
            self._run_write(self._install_agents, "Appended to target file")
        elif self._format == FORMAT_AGENTS:
            self._run_write(self._write_addendum, "Wrote paste-ready text")
        else:
            self._run_write(self._write_skill, "Generated skill")

    def _run_write(self, fn: Callable[[], str], label: str) -> None:
        self.query_one("#done-status", Static).update(f"[dim]{label} ...[/]")
        self.run_worker(lambda: self._background_write(fn), thread=True, exclusive=True)

    def _background_write(self, fn: Callable[[], str]) -> None:
        try:
            message = fn()
        except Exception as exc:
            self.call_from_thread(self._on_write_done, False, f"{type(exc).__name__}: {exc}")
        else:
            self.call_from_thread(self._on_write_done, True, message)

    def _on_write_done(self, ok: bool, message: str) -> None:
        self.query_one("#done-status", Static).update(
            escape(message) if ok else f"[red]{escape(message)}[/]"
        )

    def _install_agents(self) -> str:
        path = self._target_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(self._payload())
        return f"Appended {len(self._selected)} rule(s) to {path}"

    def _write_addendum(self) -> str:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        target = OUTPUT_DIR / "agents-md-addendum.md"
        target.write_text(self._payload(), encoding="utf-8")
        return f"Wrote paste-ready text to {target}"

    def _write_skill(self) -> str:
        SKILL_DIR.mkdir(parents=True, exist_ok=True)
        parts = [
            "---",
            "name: efficient-agent-workflow",
            "description: Named rules for batching file writes and reducing tool-call overhead.",
            "---",
            "",
            "# Efficient Agent Workflow",
            "",
        ]
        for rule in RULES:
            if rule.key in self._selected and rule.key in self._blocks:
                parts.append(f"## {rule.name}")
                parts.append("")
                parts.append(self._blocks[rule.key].rstrip("\n"))
                parts.append("")
        (SKILL_DIR / "SKILL.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
        copied = 0
        for rule in RULES:
            source = REF_DIR / rule.filename
            if rule.key in self._selected and source.exists():
                shutil.copy2(source, SKILL_DIR / rule.filename)
                copied += 1
        return f"Wrote SKILL.md and {copied} rule file(s) to {SKILL_DIR}"

    def _copy_output(self) -> None:
        text = self._payload()
        try:
            self.copy_to_clipboard(text)
        except Exception as exc:
            self.notify(f"Clipboard unavailable: {exc}", severity="error")
        else:
            self.notify("Copied selected rules to clipboard", severity="information")

    def _open_output(self) -> None:
        def opener() -> None:
            try:
                if hasattr(os, "startfile"):
                    os.startfile(str(OUTPUT_DIR if OUTPUT_DIR.exists() else ROOT))
            except Exception as exc:
                self.call_from_thread(self.notify, f"Could not open folder: {exc}", severity="error")

        self.run_worker(opener, thread=True, exclusive=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "next-format": self.action_next,
            "next-rules": self.action_next,
            "finish": self.action_next,
            "back-rules": self.action_back,
            "back-deliver": self.action_back,
            "select-all": self.action_select_all,
            "select-none": self.action_select_none,
            "btn-quit": self.action_quit_app,
            "btn-copy": self._copy_output,
            "btn-open": self._open_output,
        }
        action = actions.get(event.button.id or "")
        if action is not None:
            action()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        if event.radio_set.id == "fmt":
            self._format = FORMAT_SKILL if event.pressed.id == "fmt-skill" else FORMAT_AGENTS
            self._update_format_detail()
        elif event.radio_set.id == "auto":
            self._auto = event.pressed.id == "auto-yes"
            self._sync_delivery()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if not event.checkbox.id or not event.checkbox.id.startswith("rule-"):
            return
        key = event.checkbox.id[5:]
        if event.value:
            self._selected.add(key)
        else:
            self._selected.discard(key)
        self._update_count()
        self._update_payload()
        self._show_preview(key)

    def on_focus(self, event: Focus) -> None:
        control = event.control
        if isinstance(control, Checkbox) and control.id and control.id.startswith("rule-"):
            self._show_preview(control.id[5:])


if __name__ == "__main__":
    QuestionnaireApp().run()
