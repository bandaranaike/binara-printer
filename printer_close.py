"""Safe printer-handle cleanup shared by all Windows print jobs."""

from contextlib import contextmanager
from typing import Iterator

import win32print

from printer_config import get_printer_name


def close_printer(printer_handle) -> None:
    """Close an open Windows printer handle, if one exists."""
    if printer_handle is not None:
        win32print.ClosePrinter(printer_handle)


@contextmanager
def configured_printer() -> Iterator[object]:
    """Open the configured printer and always close its handle."""
    printer_handle = None
    try:
        printer_handle = win32print.OpenPrinter(get_printer_name())
        yield printer_handle
    finally:
        close_printer(printer_handle)
