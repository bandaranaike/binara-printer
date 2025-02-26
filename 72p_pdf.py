from reportlab.pdfgen import canvas

def generate_low_res_pdf(file_path):
    c = canvas.Canvas(file_path, pagesize=(8.5 * 72, 11 * 72))  # Letter size at 72 DPI
    c.setFont("Courier", 10)  # Use a monospaced font for compatibility

    # Write text content
    c.drawString(50, 750, "Invoice")
    c.drawString(50, 730, "Customer Name: John Doe")
    c.drawString(50, 710, "Item A: $10.00")
    c.drawString(50, 690, "Item B: $15.50")
    c.drawString(50, 670, "Total: $25.50")

    # Save the PDF
    c.save()

# Example usage
generate_low_res_pdf("invoice.pdf")
