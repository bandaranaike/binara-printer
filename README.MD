Set PM2 
```shell

pip install fastapi
pip install pydantic
pip install pywin32
pip install reportlab
pip install uvicorn
pip install pywin32
```

```pm2 start printer-run.py --name binara-print-app --interpreter python```

## Configuration and project notes

The active Windows printer is configured in `config/printer_config.json`.
Change only the `printer_name` value there, then restart the service. The
project knowledge center is in `.knowledge/PROJECT.md` and
`.knowledge/PRINTERS.md`.

For the required shared `PRINT_AGENT_TOKEN` setup between Python and Electron,
see `.knowledge/ELECTRON_PRINTER_SECURITY.md`.
