import win32print
import win32ui
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.binara.live"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PrintRequest(BaseModel):
    bill_reference : str
    payment_type : str
    bill_id : int
    customer_name : str
    doctor_name : str
    items : list[dict]
    total : str

# Directory for saving generated text files
OUTPUT_DIR = "bills"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class PrintRequest(BaseModel):
    bill_reference: str
    payment_type: str
    bill_id: int
    customer_name: str
    doctor_name: str
    items: list[dict]
    total: str

@app.post("/print")
def print_bill(request: PrintRequest):
    try:
        printer_name = "EPSON LQ-310"
        hPrinter = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(hPrinter, 2)
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

        now = datetime.now()
        at = now.strftime("%d/%m/%Y %H:%M:%S")

        x = 50  # shift to the left (1 cm ~ 100-120 units for LQ-310)
        y = 100

        # Title
        pdc.SelectObject(font_bold)
        pdc.TextOut(x, y, "BINARA MEDICAL CENTRE")
        y += 55

        pdc.SelectObject(font_normal)
        pdc.TextOut(x, y, f"Bill No.: {request.bill_id}{'-' if request.bill_reference else ''}{request.bill_reference}    {at}")
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
        y += 50

        pdc.TextOut(x, y, "No.82, New Town, Kundasale.")
        y += 30
        pdc.TextOut(x, y, "Tel: 0817213239/0812421942, Fax:0812421942")
        y += 30
        pdc.TextOut(x, y, "Email: binara82@gmail.com")

        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()

        return {"status": "success", "message": "Printed without popup via device context"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
