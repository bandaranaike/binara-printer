import win32print
import win32ui
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import logging

from printer_close import close_printer
from printer_config import get_printer_name
from security import require_print_agent_token

router = APIRouter()
logger = logging.getLogger(__name__)

# Directory for saving generated text files
OUTPUT_DIR = "bills"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class PrintRequest(BaseModel):
    bill_reference: str = Field(default="", max_length=100)
    payment_type: str = Field(max_length=50)
    bill_id: int = Field(ge=1)
    customer_name: str = Field(max_length=200)
    doctor_name: str = Field(default="", max_length=200)
    items: list[dict] = Field(min_length=1, max_length=100)
    total: str = Field(max_length=50)

@router.post("/print")
def print_bill(request: PrintRequest, _: None = Depends(require_print_agent_token)):
    pdc = None
    h_printer = None
    try:
        printer_name = get_printer_name()
        h_printer = win32print.OpenPrinter(printer_name)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)
        pdc.StartDoc("Bill Print")
        pdc.StartPage()

        font_bold = win32ui.CreateFont({
            "name": "Courier New",
            "height": 45,
            "weight": 700
        })
        font_normal = win32ui.CreateFont({
            "name": "Courier New",
            "height": 30
        })
        font_small = win32ui.CreateFont({
            "name": "Courier New",
            "height": 26
        })

        now = datetime.now()
        at = now.strftime("%d/%m/%Y %H:%M:%S")

        x = 30  # shift to the left (1 cm ~ 100-120 units for LQ-310)
        y = 30

        # Title
        pdc.SelectObject(font_bold)
        pdc.TextOut(x, y, "BINARA MEDICAL & DENTAL CENTRE")
        y += 60

        pdc.SelectObject(font_normal)
        pdc.TextOut(x, y, f"Bill No.: {request.bill_id}    {at}")
        y += 40
        pdc.TextOut(x, y, f"Customer: {request.customer_name}")
        y += 40

        if request.doctor_name:
            pdc.TextOut(x, y, f"Doctor: {request.doctor_name}")
            y += 40

        y += 30
        pdc.TextOut(x, y, "Services:")
        y += 40

        for item in request.items:
            pdc.TextOut(x, y, f"{item['name']} - Rs.{item['price']}")
            y += 40

        y += 20
        pdc.TextOut(x, y, f"Total: Rs.{request.total}")
        y += 40
        pdc.TextOut(x, y, f"Payment type: {request.payment_type}")
        y += 60

        pdc.SelectObject(font_small)
        pdc.TextOut(x, y, "No.82, New Town, Kundasale.")
        y += 30
        pdc.TextOut(x, y, "Tel: 0812424499/0706421421/0742666794, Fax:0812421942")
        y += 30
        pdc.TextOut(x, y, "https://www.binara.live  binara82@gmail.com")

        pdc.EndPage()
        pdc.EndDoc()

        return {"status": "success", "message": "Printed without popup via device context"}

    except Exception:
        logger.exception("Bill printing failed")
        raise HTTPException(status_code=500, detail="Printing failed")
    finally:
        try:
            if pdc is not None:
                pdc.DeleteDC()
        finally:
            close_printer(h_printer)
