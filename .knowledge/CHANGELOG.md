# Knowledge-center change log

## 2026-08-04

- Added shared printer configuration and printer-handle cleanup.
- Documented EPSON LQ-310 and Microsoft Print to PDF behavior.
- Secured the local Electron-to-printer boundary with loopback binding,
  per-machine token authentication, request limits, and generic print errors.
- Added the Electron integration contract in
  `ELECTRON_PRINTER_SECURITY.md`.
- Added authenticated status, pause, resume, queue-clear, queue-reset, and
  connection-close operations in `PRINTER_TASKS.md`.
- Added step-by-step shared `PRINT_AGENT_TOKEN` provisioning for Python and
  Electron using Windows Credential Manager.
