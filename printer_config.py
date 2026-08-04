"""Shared printer configuration for the Windows printing service."""

import json
from pathlib import Path


CONFIG_FILE = Path(__file__).resolve().parent / "config" / "printer_config.json"


def get_printer_name() -> str:
    """Return the configured Windows printer name.

    Change ``config/printer_config.json`` when the active printer changes;
    printing modules do not need to be edited.
    """
    try:
        with CONFIG_FILE.open(encoding="utf-8") as config_file:
            printer_name = json.load(config_file).get("printer_name", "").strip()
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Unable to read printer configuration: {CONFIG_FILE}") from exc

    if not printer_name:
        raise RuntimeError(f"The printer_name setting is empty in {CONFIG_FILE}")
    return printer_name
