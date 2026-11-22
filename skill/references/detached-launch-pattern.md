- **Launch pattern for long runs**: detached via WMI `Win32_Process Create`
  (crash-safe), capture PID once, hand monitoring to a watcher script
  (`%TEMP%\opencode\wait_probe.ps1 -Tag <tag>` → writes `<tag>_final.txt`).
