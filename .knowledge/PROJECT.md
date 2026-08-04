# Printer service knowledge center

## Purpose

This is a small FastAPI service for printing bills and service-cost reports
from a Windows machine. It supports both an EPSON LQ-310 dot-matrix printer
and Microsoft Print to PDF, depending on the configured Windows printer.

## Main files

- `printer-run.py` starts Uvicorn on port 5000.
- `main.py` creates the FastAPI application and registers routes.
- `print_bill.py` exposes `POST /print`.
- `print_summary.py` exposes `POST /print-summary`.
- `printer_config.py` reads the shared printer setting.
- `printer_close.py` owns printer-handle cleanup and the configured-printer
  context manager.
- `config/printer_config.json` is the operator-editable configuration file.
- `raw_print.c` and `raw_print_cpp.cpp` are standalone experimental Windows
  RAW-print examples; they are not used by the FastAPI service.

## Changing the active printer

Edit only `config/printer_config.json`, for example:

```json
{
  "printer_name": "EPSON LQ-310"
}
```

The value must exactly match the printer name shown in Windows. Restart the
service after changing it.

## Important conventions

- Windows printer handles must be closed in a `finally` path. Use
  `configured_printer()` for new print code.
- The Python printer agent is local-only and must bind to `127.0.0.1`; it must
  not be exposed through a router, public IP, or `0.0.0.0`.
- Every print request requires the per-machine `PRINT_AGENT_TOKEN` in the
  `X-Print-Agent-Token` header. Electron should send it only from its main
  process, never from renderer code.
- The token is generated once per Windows machine, configured as a Python
  user/system environment variable, and stored for Electron in Windows
  Credential Manager. It must never be committed to source control.
- Read `.knowledge/ELECTRON_PRINTER_SECURITY.md` before changing the Electron
  integration or printer API.
- Read `.knowledge/PRINTER_TASKS.md` for the complete authenticated endpoint
  contract and the meaning of queue-control operations.
- Keep generated files in `bills/` or `reports/`; these folders are ignored by
  Git.
- Do not delete the C/C++ examples until confirming that no external process
  or operator workflow still compiles or runs them.

## Knowledge-center maintenance

When a task changes architecture, security, printer behavior, configuration,
deployment, or troubleshooting, update the relevant file in `.knowledge/` in
the same change. Add a dated entry to `.knowledge/CHANGELOG.md` when the
change introduces a new operational rule or integration contract.
