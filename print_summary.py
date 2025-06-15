import win32print
import win32ui
from datetime import datetime
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

router = APIRouter()

class ServiceCostItem(BaseModel):
    service_name: str
    quantity: int
    total: float | str

class PrintRequest(BaseModel):
    start_date: str
    end_date: str
    items: list[ServiceCostItem]

# Create output directory if needed
OUTPUT_DIR = "reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Wrap text based on max characters
def wrap_text(text: str, max_chars: int):
    lines = []
    while len(text) > max_chars:
        space_pos = text.rfind(" ", 0, max_chars)
        if space_pos == -1:
            space_pos = max_chars
        lines.append(text[:space_pos])
        text = text[space_pos:].lstrip()
    lines.append(text)
    return lines

@router.post("/print-summary")
def print_service_cost(request: PrintRequest):
    try:
        # Setup
        printer_name = "MSPrintPDF"  # Replace with your printer name
        # printer_name = "EPSON LQ-310"  # Replace with your printer name
        hPrinter = win32print.OpenPrinter(printer_name)
        win32print.GetPrinter(hPrinter, 2)  # Just to confirm printer is accessible
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)
        pdc.StartDoc("Service Cost Report")
        pdc.StartPage()

        # Define fonts
        font_bold = win32ui.CreateFont({
            "name": "Courier New",
            "height": 40,
            "weight": 700
        })
        font_normal = win32ui.CreateFont({
            "name": "Courier New",
            "height": 28
        })
        font_small = win32ui.CreateFont({
            "name": "Courier New",
            "height": 26
        })

        now = datetime.now()
        printed_at = now.strftime("%d/%m/%Y %H:%M:%S")

        # Printable width
        max_line_width = 576  # 6 inches * 96 DPI
        char_width = 7
        max_chars_per_line = max_line_width // char_width  # ~82

        # Column widths (characters)
        service_name_width = 26
        qty_width = 10
        total_width = 12

        x = 30  # Left margin
        y = 30  # Top starting point

        # Header
        pdc.SelectObject(font_bold)
        pdc.TextOut(x, y, "SERVICE COST REPORT")
        y += 55

        pdc.SelectObject(font_normal)
        pdc.TextOut(x, y, f"Date Range: {request.start_date} to {request.end_date}")
        y += 40
        pdc.TextOut(x, y, f"Generated: {printed_at}")
        y += 40

        pdc.SelectObject(font_small)
        pdc.TextOut(x, y, "Service Name".ljust(service_name_width) + "Qty".ljust(qty_width) + "Total".rjust(total_width))
        y += 30
        pdc.TextOut(x, y, "-" * (service_name_width + qty_width + total_width))
        y += 30

        total_quantity = 0
        grand_total = 0.0

        for item in request.items:
            wrapped_lines = wrap_text(item.service_name, service_name_width)
            for i, line in enumerate(wrapped_lines):
                qty = str(item.quantity).rjust(qty_width) if i == 0 else "".rjust(qty_width)
                total_amt = f"{item.total}".rjust(total_width) if i == 0 else "".rjust(total_width)
                pdc.TextOut(x, y, f"{line.ljust(service_name_width)}{qty}{total_amt}")
                y += 30

            total_quantity += item.quantity
            grand_total += float(item.total)

        y += 40
        pdc.SelectObject(font_normal)
        pdc.TextOut(x, y, f"Total Quantity: {total_quantity}")
        y += 30
        pdc.TextOut(x, y, f"Grand Total: Rs.{grand_total:.2f}")

        # End
        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()

        return {"status": "success", "message": "Service cost report printed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

