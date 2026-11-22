- **NEVER repeat a status/monitoring command "just to check".** If a long run
  needs watching, write ONE detached script that polls internally and exits
  itself on a completion condition; then read its single output file at natural
  checkpoints (user ping / todo continuation), at most ONE check per activation.
