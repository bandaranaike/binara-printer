import win32print
# win32ui is not strictly necessary for this RAW printing task but kept from original
import win32ui
from datetime import datetime

# --- Configuration ---
# Ensure this matches the name in your Windows printer settings
PRINTER_NAME = "EPSON-LQ-310"

# --- ESC/P Commands (as bytes) ---
ESC = b'\x1b'  # Escape character
AT = b'@'     # @ symbol

# Initialize Printer (resets to default settings)
CMD_INIT_PRINTER = ESC + AT

# Set Line Spacing to 1/6 inch (common default, good starting point)
# Other options exist, e.g., ESC '0' for 1/8 inch
CMD_SET_LINE_SPACING_1_6 = ESC + b'2'

# Set Page Length in Lines
# For 5-inch paper:
# If Line Spacing is 1/6 inch (6 lines per inch): 5 inches * 6 LPI = 30 lines
# If Line Spacing is 1/8 inch (8 lines per inch): 5 inches * 8 LPI = 40 lines
# Adjust 'PAGE_LENGTH_IN_LINES' based on your printer's LPI and desired layout.
PAGE_LENGTH_IN_LINES = 30  # Example for 5 inches at 6 LPI
# ESC C n (n = number of lines, 1-127). For n > 127, use ESC C NUL n.
if 1 <= PAGE_LENGTH_IN_LINES <= 127:
    CMD_SET_PAGE_LENGTH = ESC + b'C' + bytes([PAGE_LENGTH_IN_LINES])
else:
    # For n > 127 (up to 255), use ESC C NUL n
    CMD_SET_PAGE_LENGTH = ESC + b'C' + b'\x00' + bytes([PAGE_LENGTH_IN_LINES])


# Form Feed (ejects the current page)
FF = b'\x0c'

def print_bill(data):
    hPrinter = win32print.OpenPrinter(PRINTER_NAME)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Binara Medical Bill", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)

        # --- Prepare text data (same as your original code) ---
        lines = []
        lines.append("  Binara Medical Centre\n")
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        lines.append(f"  Bill No.: {data['bill_id']}{'-' if data['bill_reference'] else ''}{data['bill_reference']}    {now}\n")
        lines.append(f"  Customer: {data['customer_name']}\n")

        if data['doctor_name']:
            lines.append(f"  Doctor: {data['doctor_name']}\n")

        lines.append("\n  Services:\n")
        for item in data['items']:
            # Consider character width limits of 5-inch paper here.
            # You might need to format strings to fit (e.g., fixed-width columns).
            lines.append(f"    {item['name']} - Rs.{item['price']}\n")

        lines.append("\n")
        lines.append(f"  Total: Rs.{data['total']}       Payment type: {data['payment_type']}\n")
        lines.append("\n")
        lines.append("  No.82, New Town, Kundasale.\n")
        lines.append("  Tel: 0817213239/0812421942, Fax:0812421942\n")
        lines.append("  Email: binara82@gmail.com\n")
        # Add a few blank lines if needed before form feed for bottom margin
        # lines.append("\n\n")

        text_content = "".join(lines)

        # Encode text content. 'utf-8' is modern, but for very old dot matrix printers,
        # 'cp437' or another specific codepage might be more compatible if you see issues
        # with special characters. For standard text, 'utf-8' producing ASCII bytes is fine.
        encoded_text = text_content.encode('ascii')

        # --- Combine ESC/P commands and data ---
        # 1. Initialize printer
        # 2. Set desired line spacing (optional if default is okay, but good to be explicit)
        # 3. Set page length
        # 4. Add text data
        # 5. Add Form Feed to eject page
        data_to_send = (CMD_INIT_PRINTER +
                        CMD_SET_LINE_SPACING_1_6 +
                        CMD_SET_PAGE_LENGTH +
                        encoded_text +
                        FF)

        win32print.WritePrinter(hPrinter, data_to_send)

        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)

# Example usage (same as your original code)
if __name__ == "__main__":
    sample = {
        "bill_reference": "A",
        "payment_type": "Cash",
        "bill_id": 123,
        "customer_name": "Eranda B.",
        "doctor_name": "Dr. Silva",
        "items": [{"name": "Consultation", "price": "1500"}, {"name": "Injection", "price": "500"}],
        "total": "2000"
    }
    print_bill(sample)
    print(f"Sent print job for 5-inch paper (approx. {PAGE_LENGTH_IN_LINES} lines).")