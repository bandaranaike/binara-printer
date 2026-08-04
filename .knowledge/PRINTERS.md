# Printer notes

## EPSON LQ-310

Use the exact installed Windows queue name. The device is a dot-matrix
printer, so test paper size, line spacing, margins, and page feed on the real
machine.

## Microsoft Print to PDF

PDF printing can invoke Windows output behavior depending on the queue and
driver settings. It is useful for development and verification, but it does
not validate all EPSON-specific paper behavior.

## Before troubleshooting

1. Confirm the queue exists in Windows with the exact configured name.
2. Confirm the Windows account running Uvicorn can access that queue.
3. Check the API response and the Uvicorn console for the underlying Windows
   error.
