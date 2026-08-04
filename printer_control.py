"""Authenticated local controls for the configured Windows printer queue."""

import logging

import win32print
from fastapi import APIRouter, Depends, HTTPException

from printer_close import close_printer
from printer_config import get_printer_name
from security import require_print_agent_token


router = APIRouter(prefix="/printer", tags=["printer-control"])
logger = logging.getLogger(__name__)


def _open_configured_printer():
    return win32print.OpenPrinter(get_printer_name())


def _printer_status(info: dict) -> dict:
    status = info.get("Status", 0)
    status_names = {
        win32print.PRINTER_STATUS_PAUSED: "paused",
        win32print.PRINTER_STATUS_ERROR: "error",
        win32print.PRINTER_STATUS_PENDING_DELETION: "pending_deletion",
        win32print.PRINTER_STATUS_PAPER_JAM: "paper_jam",
        win32print.PRINTER_STATUS_PAPER_OUT: "paper_out",
        win32print.PRINTER_STATUS_MANUAL_FEED: "manual_feed",
        win32print.PRINTER_STATUS_PAPER_PROBLEM: "paper_problem",
        win32print.PRINTER_STATUS_OFFLINE: "offline",
        win32print.PRINTER_STATUS_BUSY: "busy",
        win32print.PRINTER_STATUS_PRINTING: "printing",
        win32print.PRINTER_STATUS_OUTPUT_BIN_FULL: "output_bin_full",
        win32print.PRINTER_STATUS_NOT_AVAILABLE: "not_available",
        win32print.PRINTER_STATUS_WAITING: "waiting",
        win32print.PRINTER_STATUS_PROCESSING: "processing",
        win32print.PRINTER_STATUS_INITIALIZING: "initializing",
        win32print.PRINTER_STATUS_WARMING_UP: "warming_up",
        win32print.PRINTER_STATUS_TONER_LOW: "toner_low",
        win32print.PRINTER_STATUS_NO_TONER: "no_toner",
        win32print.PRINTER_STATUS_USER_INTERVENTION: "user_intervention",
        win32print.PRINTER_STATUS_DOOR_OPEN: "door_open",
        win32print.PRINTER_STATUS_SERVER_UNKNOWN: "server_unknown",
        win32print.PRINTER_STATUS_POWER_SAVE: "power_save",
    }
    names = [name for bit, name in status_names.items() if status & bit]
    return {
        "status_code": status,
        "status": names or ["ready"],
        "job_count": info.get("cJobs", 0),
        "printer_name": info.get("pPrinterName") or get_printer_name(),
        "printer_state": info.get("pStatus") or "",
    }


def _run_printer_command(command: int, action: str) -> dict:
    handle = None
    try:
        handle = _open_configured_printer()
        info = win32print.GetPrinter(handle, 2)
        win32print.SetPrinter(handle, 0, None, command)
        return {"status": "success", "action": action, **_printer_status(info)}
    except Exception:
        logger.exception("Printer control action failed: %s", action)
        raise HTTPException(status_code=500, detail="Printer control failed")
    finally:
        close_printer(handle)


@router.get("/status")
def printer_status(_: None = Depends(require_print_agent_token)):
    """Return queue and Windows printer status without changing the queue."""
    handle = None
    try:
        handle = _open_configured_printer()
        return _printer_status(win32print.GetPrinter(handle, 2))
    except Exception:
        logger.exception("Unable to read printer status")
        raise HTTPException(status_code=500, detail="Unable to read printer status")
    finally:
        close_printer(handle)


@router.post("/pause")
def pause_printer(_: None = Depends(require_print_agent_token)):
    return _run_printer_command(win32print.PRINTER_CONTROL_PAUSE, "pause")


@router.post("/resume")
def resume_printer(_: None = Depends(require_print_agent_token)):
    return _run_printer_command(win32print.PRINTER_CONTROL_RESUME, "resume")


@router.post("/clear-queue")
def clear_printer_queue(_: None = Depends(require_print_agent_token)):
    """Permanently remove all queued jobs for this printer."""
    return _run_printer_command(win32print.PRINTER_CONTROL_PURGE, "clear_queue")


@router.post("/reset")
def reset_printer_queue(_: None = Depends(require_print_agent_token)):
    """Clear queued jobs and resume the queue; this is not a hardware reboot."""
    result = _run_printer_command(win32print.PRINTER_CONTROL_PURGE, "reset_clear_queue")
    resume_result = _run_printer_command(win32print.PRINTER_CONTROL_RESUME, "reset_resume")
    result.update({"status": resume_result.get("status"), "status_after_reset": resume_result})
    return result


@router.post("/close")
def close_printer_connection(_: None = Depends(require_print_agent_token)):
    """Open and immediately close a test handle; it does not power off the device."""
    handle = None
    try:
        handle = _open_configured_printer()
        return {"status": "success", "action": "connection_closed", "printer_name": get_printer_name()}
    except Exception:
        logger.exception("Unable to open printer for close operation")
        raise HTTPException(status_code=500, detail="Unable to access printer")
    finally:
        close_printer(handle)
