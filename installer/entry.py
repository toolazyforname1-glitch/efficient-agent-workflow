"""Standalone entry point: relaunch the questionnaire minimized, then run the TUI."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if "--selftest" in sys.argv:
    from questionnaire import REF_DIR, RULES

    missing = [r.filename for r in RULES if not (REF_DIR / r.filename).is_file()]
    assert not missing, f"missing bundled rules: {missing}"
    print(f"SELFTEST OK rules={len(RULES)} refdir={REF_DIR}")
elif "--tui" in sys.argv:
    from questionnaire import QuestionnaireApp

    QuestionnaireApp().run()
else:
    if getattr(sys, "frozen", False):
        args = [sys.executable, "--tui"]
    else:
        args = [sys.executable, str(Path(__file__).with_name("questionnaire.py"))]
    if sys.platform == "win32":
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 6  # SW_MINIMIZE
        subprocess.Popen(args, startupinfo=startup)
    else:
        subprocess.Popen(args)
