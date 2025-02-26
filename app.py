from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from fastapi.middleware.cors import CORSMiddleware
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.binara.live"],  # Replace with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model for the print request
class PrintRequest(BaseModel):
    bill_reference : str
    payment_type : str
    bill_id : int
    customer_name : str
    doctor_name	: str
    items : list[dict]  # Example: [{"name": "Item A", "price": 10.0}, {"name": "Item B", "price": 20.0}]
    total : str

# Directory for saving generated PDFs
OUTPUT_DIR = "bills"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/print")
def print_bill(request: PrintRequest):
    try:
        pdfmetrics.registerFont(TTFont('CodeSaver', 'fonts/CodeSaver-Regular.ttf'))

        # File path for the PDF
        file_path = os.path.join(OUTPUT_DIR, f"bill_{request.bill_id}{'-' if request.bill_reference else ''}{request.bill_reference}.pdf")

        # Generate PDF
        c = canvas.Canvas(file_path)
        x_position = 50
        y_position = 800

        c.setFont("CodeSaver", 16)
        c.drawString(x_position, y_position, f"Binara Medical Centre")
        y_position -= 30

        c.setFont("CodeSaver", 12)

        now  = datetime.now()
        at = now.strftime("%d/%m/%Y %H:%M:%S")

        # Bill header
        c.drawString(x_position, y_position, f"Bill No.: {request.bill_id}{'-' if request.bill_reference else ''}{request.bill_reference}")
        c.drawString(x_position + 150, y_position, at)
        y_position -= 20
        c.drawString(x_position, y_position, f"Customer: {request.customer_name}")
        y_position -= 20

        if request.doctor_name:
            c.drawString(x_position, y_position, f"Doctor: {request.doctor_name}")
            y_position -= 20

        y_position -= 10
        c.drawString(x_position, y_position, "Services:")
        y_position -= 20

        # Items
        for item in request.items:
            c.drawString(x_position + 20, y_position, f"{item['name']} - Rs.{item['price']}")
            y_position -= 20

        y_position -= 10
        # Total
        c.drawString(x_position, y_position, f"Total: Rs.{request.total}")

        c.setFont("CodeSaver", 10)

        c.drawString(x_position + 200, y_position, f"Payment type: {request.payment_type}")
        y_position -= 30

        c.setFont("CodeSaver", 10)
        c.drawString(x_position, y_position, "No.82, New Town, Kundasale.")
        y_position -= 16
        c.drawString(x_position, y_position, "Tel: 0817213239/0812421942, Fax:0812421942")
        y_position -= 16
        c.drawString(x_position, y_position, "Email: binara82@gmail.com")
        c.save()

        return {"status": "success", "message": "PDF generated", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
