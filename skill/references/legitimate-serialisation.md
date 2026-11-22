**WHEN SERIALISING IS LEGITIMATE (only these cases):**
- File B's content genuinely depends on a value read from file A or from a command output (generated code, a version string, a test result).
- A SINGLE file too large for one `write` call — build it with successive `edit`/append calls. That is one file; it never justifies serialising OTHER independent files.
- A tool result is required before the next step (test output, build error, search hit).
