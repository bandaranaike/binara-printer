# Printer task contract for Electron and AI agents

This is the complete task reference for the local Python printer agent.
Electron must call these endpoints from its **main process** only.

## Connection and authentication

Base URL:

```text
http://127.0.0.1:5000
```

Every request must include:

```http
X-Print-Agent-Token: <PRINT_AGENT_TOKEN>
```

The token is a per-Windows-machine secret. Do not send it from renderer code,
do not put it in URLs, and do not log it.

Provisioning is documented in `ELECTRON_PRINTER_SECURITY.md` under “Token
provisioning for both applications”. The Python agent reads
`PRINT_AGENT_TOKEN` from the Windows environment. Electron should store the
identical token in Windows Credential Manager through `keytar`.

Common JavaScript helper:

```javascript
const PRINTER_URL = "http://127.0.0.1:5000";

async function printerRequest(path, method, body) {
  const response = await fetch(`${PRINTER_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      "X-Print-Agent-Token": await getPrinterToken()
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) })
  });

  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(`Printer request failed: HTTP ${response.status}`);
  }
  return result;
}
```

`getPrinterToken()` must read from the main process or Windows Credential
Manager. It must never read a renderer variable supplied by a webpage.

## Print a bill

```http
POST /print
```

Example body:

```json
{
  "bill_reference": "BILL-2026-001",
  "payment_type": "Cash",
  "bill_id": 1,
  "customer_name": "Customer name",
  "doctor_name": "Doctor name",
  "items": [
    {"name": "Consultation", "price": "1500.00"}
  ],
  "total": "1500.00"
}
```

Use this only after Laravel has authenticated the user and authorized the
bill. Add an idempotency check in Laravel so retries do not print duplicates.

## Print a service summary

```http
POST /print-summary
```

Example body:

```json
{
  "start_date": "2026-08-01",
  "end_date": "2026-08-04",
  "items": [
    {"service_name": "Consultation", "quantity": 3, "total": 4500}
  ]
}
```

## Read printer status

```http
GET /printer/status
```

Response fields include:

- `status`: one or more Windows states, or `ready`.
- `status_code`: raw Windows status bitmask.
- `job_count`: jobs currently in the queue.
- `printer_name`: configured Windows queue name.
- `printer_state`: optional Windows status text.

Use this before showing printer controls or retrying a failed print.

## Pause and resume

```http
POST /printer/pause
POST /printer/resume
```

Pause stops the queue from processing jobs. Resume allows queued jobs to
continue. These operations do not delete queued jobs.

## Clear the queue

```http
POST /printer/clear-queue
```

This permanently removes all jobs currently queued for the configured printer.
The Electron UI must require explicit confirmation before calling it.

## Reset the printer queue

```http
POST /printer/reset
```

Reset means **clear all queued jobs, then resume the queue**. It is not a
hardware reboot and does not restart Windows Print Spooler.

## Close printer connection

```http
POST /printer/close
```

This opens a short-lived Windows printer handle and closes it immediately. It
confirms that the queue can be accessed and releases the handle. It does not
power off, disconnect, or restart the physical printer.

Normal bill and summary requests already close their Windows handles in a
`finally` block. Electron usually does not need to call this endpoint.

## Hardware and spooler restart

The Windows print API does not provide a safe, ordinary printer-device reboot.
Restarting the Windows `Spooler` service affects every printer on the computer,
can require Administrator privileges, and must not be exposed as a localhost
HTTP endpoint. If a true spooler restart is ever required, perform it through
an administrator-controlled Windows service or an operator action outside this
API.

## Error handling

- `401`: token missing or invalid; do not retry repeatedly.
- `422`: request validation failed; fix the payload.
- `500`: Windows printer operation failed; show a generic message and inspect
  the local agent log.

AI agents must not automatically call `clear-queue` or `reset` after an
ordinary print failure because those operations can destroy other users'
queued print jobs.

## Electron security requirements

- Use `nodeIntegration: false`, `contextIsolation: true`, and `sandbox: true`.
- Restrict IPC to named functions such as `printBill`, `printerStatus`, and
  `resumePrinter`.
- Validate all IPC arguments in the main process.
- Do not expose arbitrary URLs, `ipcRenderer.send`, Node APIs, or the token to
  the renderer.
- Keep the agent bound to `127.0.0.1`; never change it to `0.0.0.0` for remote
  access.
