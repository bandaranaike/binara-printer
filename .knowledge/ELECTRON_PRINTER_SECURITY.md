# Electron printer security integration guide

This document is an implementation contract for an Electron application that
uses the local Python printer agent.

## Security model

The Python agent listens only on:

```text
http://127.0.0.1:5000
```

It must not listen on `0.0.0.0`, the computer's LAN IP, or a public domain.
Every print request must include the same per-machine secret in this header:

```text
X-Print-Agent-Token: <secret>
```

The Laravel server should authenticate the user and authorize the print job.
The Electron main process then sends the authorized job to the local agent.
The browser renderer must never call the printer agent directly.

## Token provisioning for both applications

Generate one different token for each Windows computer. Use that same token in
the Python printer agent and the Electron **main process**. Do not generate a
different token for each request.

Open PowerShell as the same Windows user that runs both applications and run:

```powershell
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$rng.Dispose()
$token = [Convert]::ToBase64String($bytes)
[Environment]::SetEnvironmentVariable('PRINT_AGENT_TOKEN', $token, 'User')
$token
```

Copy the printed token to a secure temporary location. This is the only time
it should be displayed during setup.

### Set it for the Python printer agent

The command above stores `PRINT_AGENT_TOKEN` in the current user's Windows
environment. Close and reopen PowerShell, then restart PM2:

```powershell
pm2 restart binara-print-app --update-env
```

If PM2 runs under another Windows account, set the variable for that account
or use the Windows System environment. Do not put the token in
`printer_config.json`, Python source files, or Git.

The agent refuses to start unless the token is at least 32 characters long.

### Set it for the Electron application

Store the same token using Windows Credential Manager. The recommended
Electron implementation uses the `keytar` package from the main process:

```powershell
npm install keytar
```

During a trusted first-run setup or installer step, save the copied token:

```javascript
const keytar = require("keytar");

await keytar.setPassword(
  "BinaraPrinterAgent",
  "PRINT_AGENT_TOKEN",
  tokenFromTrustedSetupInput
);
```

Later, the main process reads it when making a printer request:

```javascript
const keytar = require("keytar");

async function getPrinterToken() {
  const token = await keytar.getPassword(
    "BinaraPrinterAgent",
    "PRINT_AGENT_TOKEN"
  );
  if (!token) throw new Error("Printer token is not configured");
  return token;
}
```

`tokenFromTrustedSetupInput` must come from a protected installer/setup screen
or secure provisioning process. Do not accept it from a remote webpage or
store it in renderer state. Never commit the token or place it in a packaged
Electron `.env` file.

### Development-only alternative

If Electron is started manually by the same Windows user, it can read
`process.env.PRINT_AGENT_TOKEN`. This is acceptable for local development, but
Windows Credential Manager is preferred for a packaged production app:

```javascript
const token = process.env.PRINT_AGENT_TOKEN;
```

Restart Electron after changing the environment variable.

### Verify the setup

With the Python agent running, use the token without placing it in a URL:

```powershell
$headers = @{ "X-Print-Agent-Token" = $env:PRINT_AGENT_TOKEN }
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/printer/status" `
  -Method Get `
  -Headers $headers
```

The expected response contains `printer_name`, `status`, and `job_count`.
A missing or incorrect token returns HTTP `401`.

To confirm only that the environment variable exists without printing it:

```powershell
[Environment]::GetEnvironmentVariable('PRINT_AGENT_TOKEN', 'User').Length
```

## Electron implementation rules

1. Make printer requests only from the Electron **main process**.
2. Keep the token in the main process or Windows Credential Manager.
3. Do not put the token in renderer JavaScript, HTML, a remote webpage, or a
   frontend build variable.
4. Expose only narrow, validated preload functions such as `printBill(data)`.
5. Set `nodeIntegration: false`, `contextIsolation: true`, and `sandbox: true`.
6. Do not allow arbitrary navigation or untrusted remote content in a window
   that has printer IPC access.
7. Validate the job in the main process before forwarding it.

## Main-process request example

```javascript
const PRINTER_URL = "http://127.0.0.1:5000";

async function printBill(job, printerToken) {
  const response = await fetch(`${PRINTER_URL}/print`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Print-Agent-Token": printerToken
    },
    body: JSON.stringify(job)
  });

  if (response.status === 401) {
    throw new Error("Printer agent authentication failed");
  }
  if (!response.ok) {
    throw new Error("Printer agent rejected the print job");
  }
  return response.json();
}
```

Use the same pattern for `POST /print-summary`. Do not accept an arbitrary URL
from the renderer; keep `127.0.0.1:5000` hard-coded or signed application
configuration.

## Preload boundary example

```javascript
// preload.js
const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("printer", {
  printBill: (job) => ipcRenderer.invoke("printer:print-bill", job),
  printSummary: (job) => ipcRenderer.invoke("printer:print-summary", job)
});
```

The IPC handlers must validate the job and call the main-process functions.
Never expose `ipcRenderer.send`, the token, Node.js APIs, or an arbitrary HTTP
request function to the renderer.

## Expected failures

- `401`: missing or incorrect `X-Print-Agent-Token`.
- `422`: request data violates validation limits.
- `500`: the authenticated request reached the agent but Windows printing
  failed; the detailed reason is logged locally, not returned to the client.

## Deployment checklist

- Confirm `printer-run.py` uses `127.0.0.1`.
- Confirm Windows Firewall/router has no inbound public rule for port 5000.
- Confirm each machine has a unique token.
- Confirm the token is not present in renderer logs, DevTools, URLs, or crash
  reports.
- Confirm Laravel performs authorization and prevents duplicate print jobs.
- Test that an unauthenticated POST receives `401`.
