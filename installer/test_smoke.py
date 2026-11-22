"""Headless smoke test for the RulePack installer TUI."""
from __future__ import annotations

import asyncio

from textual.widgets import Checkbox, RadioButton, RadioSet

from questionnaire import RULES, QuestionnaireApp


async def main() -> None:
    app = QuestionnaireApp()
    async with app.run_test(size=(118, 40)) as pilot:
        await pilot.pause()
        assert app.query_one("#fmt", RadioSet).pressed_button.id == "fmt-agents"
        assert app.query_one("#fmt-agents", RadioButton).value is True
        assert app.query_one("#fmt-skill", RadioButton).value is False
        assert len(RULES) == 15
        for rule in RULES:
            assert app.query_one(f"#rule-{rule.key}", Checkbox).value is True, rule.key
        assert app.query_one("#auto-no", RadioButton).value is True
        assert app.query_one("#auto-yes", RadioButton).value is False
        assert app.query_one("#nav-format").has_class("active")
        assert app.query_one("#pane-format").has_class("active")
        print(f"SMOKE PASS: {len(RULES)} named rules checked; AGENTS.md default; auto-install No")


if __name__ == "__main__":
    asyncio.run(main())
