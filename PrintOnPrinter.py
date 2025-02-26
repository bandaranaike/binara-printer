import win32print
import win32api

@app.post("/print")
def print_bill(request: PrintRequest):
    try:
        file_path = os.path.join(OUTPUT_DIR, f"bill_{request.bill_id}.pdf")

        # Generate PDF (as before)
        c = canvas.Canvas(file_path)
        c.setFont("Helvetica", 12)
        c.drawString(50, 800, f"Bill ID: {request.bill_id}")
        c.drawString(50, 780, f"Customer Name: {request.customer_name}")
        c.drawString(50, 760, "Items:")
        y_position = 740
        for item in request.items:
            c.drawString(70, y_position, f"{item['name']} - ${item['price']}")
            y_position -= 20
        c.drawString(50, y_position - 20, f"Total: ${request.total}")
        c.save()

        # Print the PDF using Windows default printer
        win32api.ShellExecute(0, "print", file_path, None, ".", 0)

        return {"status": "success", "message": "Bill sent to printer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
