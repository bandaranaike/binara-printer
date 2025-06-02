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

class ServiceCostItem(BaseModel):
    service_id: int
    service_name: str
    service_key: str
    total_bill_amount: float
    total_system_amount: float
    item_count: int

class PrintRequest(BaseModel):
    start_date: str
    end_date: str
    total_services: int
    total_bill_amount: float
    total_system_amount: float
    items: list[ServiceCostItem]

# Directory for saving generated text files
OUTPUT_DIR = "reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/print-service-cost")
def print_service_cost(request: PrintRequest):
    try:
        printer_name = "EPSON LQ-310"
        hPrinter = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(hPrinter, 2)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)
        pdc.StartDoc("Service Cost Report")
        pdc.StartPage()

        # Define fonts
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
            "height": 25
        })

        now = datetime.now()
        printed_at = now.strftime("%d/%m/%Y %H:%M:%S")

        x = 50  # Left margin (1 cm)
        y = 100  # Start position

        # Title
        pdc.SelectObject(font_bold)
        pdc.TextOut(x, y, "SERVICE COST REPORT")
        y += 55

        pdc.SelectObject(font_normal)
        # Date range
        pdc.TextOut(x, y, f"Date Range: {request.start_date} to {request.end_date}")
        y += 40
        pdc.TextOut(x, y, f"Generated: {printed_at}")
        y += 40

        # Summary information
        pdc.TextOut(x, y, f"Total Services: {request.total_services}")
        y += 40
        pdc.TextOut(x, y, f"Total Bill Amount: Rs.{request.total_bill_amount:.2f}")
        y += 40
        pdc.TextOut(x, y, f"Total System Amount: Rs.{request.total_system_amount:.2f}")
        y += 60

        # Table header
        pdc.SelectObject(font_bold)
        pdc.TextOut(x, y, "SERVICE DETAILS")
        y += 40

        pdc.SelectObject(font_small)
        # Column headers
        pdc.TextOut(x, y, "Service Name".ljust(30) + "ID".ljust(10) + "Items".rjust(6) + "Bill Amt".rjust(12) + "Sys Amt".rjust(12))
        y += 30
        pdc.TextOut(x, y, "-" * 70)  # Divider line
        y += 30

        # Table rows
        for item in request.items:
            service_name = item.service_name[:27] + "..." if len(item.service_name) > 30 else item.service_name.ljust(30)
            service_id = item.service_key.ljust(10)
            items = str(item.item_count).rjust(6)
            bill_amount = f"Rs.{item.total_bill_amount:.2f}".rjust(12)
            sys_amount = f"Rs.{item.total_system_amount:.2f}".rjust(12)

            pdc.TextOut(x, y, f"{service_name}{service_id}{items}{bill_amount}{sys_amount}")
            y += 30

        y += 40
        pdc.SelectObject(font_normal)
        pdc.TextOut(x, y, "End of Report")
        y += 40
        pdc.TextOut(x, y, "-" * 40)  # Footer divider

        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()

        return {"status": "success", "message": "Service cost report printed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)