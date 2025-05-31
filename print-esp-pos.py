# print_escpos.py - ESC/POS printing for Epson LQ-310

import win32print
import win32con
import time

# Printer configuration
PRINTER_NAME = "EPSON-LQ-310"  # Must match Windows printer name

# ESC/POS commands
INIT = b'\x1B\x40'  # Initialize printer
CUT = b'\x1D\x56\x00'  # Partial cut (if supported)
LF = b'\x0A'  # Line feed
BOLD_ON = b'\x1B\x45\x01'  # Bold on
BOLD_OFF = b'\x1B\x45\x00'  # Bold off
ALIGN_LEFT = b'\x1B\x61\x00'  # Left alignment
ALIGN_CENTER = b'\x1B\x61\x01'  # Center alignment
ALIGN_RIGHT = b'\x1B\x61\x02'  # Right alignment
UNDERLINE_ON = b'\x1B\x2D\x01'  # Underline on
UNDERLINE_OFF = b'\x1B\x2D\x00'  # Underline off

def send_to_printer(commands):
    """Send raw ESC/POS commands to the printer"""
    try:
        hprinter = win32print.OpenPrinter(PRINTER_NAME)
        try:
            win32print.StartDocPrinter(hprinter, 1, ("ESC/POS Print", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, commands)
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)
        return True
    except Exception as e:
        print(f"Printing error: {str(e)}")
        return False

def create_receipt():
    """Generate receipt using ESC/POS commands"""
    from datetime import datetime

    # Create command sequence
    commands = INIT  # Initialize printer

    # Header (centered, bold)
    commands += ALIGN_CENTER + BOLD_ON
    commands += b"YOUR COMPANY NAME\n"
    commands += BOLD_OFF + ALIGN_LEFT

    # Title (underline)
    commands += UNDERLINE_ON + b"RECEIPT\n" + UNDERLINE_OFF

    # Left-aligned details
    commands += b"Date: " + datetime.now().strftime("%Y-%m-%d %H:%M").encode() + LF
    commands += b"Receipt No: TEST-12345" + LF
    commands += b"-"*32 + LF  # Divider line

    # Column headers (bold)
    commands += BOLD_ON
    commands += b"ITEM".ljust(16)
    commands += b"QTY".center(6)
    commands += b"PRICE".rjust(10) + LF
    commands += BOLD_OFF
    commands += b"-"*32 + LF  # Divider line

    # Items (normal)
    commands += b"Product 1".ljust(16)
    commands += b"2".center(6)
    commands += b"$10.00".rjust(10) + LF

    commands += b"Product 2".ljust(16)
    commands += b"1".center(6)
    commands += b"$15.50".rjust(10) + LF

    commands += b"Service Fee".ljust(16)
    commands += b"1".center(6)
    commands += b"$20.00".rjust(10) + LF

    commands += b"-"*32 + LF  # Divider line

    # Total (bold, right aligned)
    commands += ALIGN_RIGHT + BOLD_ON
    commands += b"TOTAL: $45.50" + LF
    commands += BOLD_OFF + ALIGN_LEFT

    # Footer
    commands += LF*2  # Blank lines
    commands += ALIGN_CENTER
    commands += b"Thank you for your business!\n"
    commands += LF*3  # Feed paper before cut

    # Add cut command (if supported)
    commands += CUT

    return commands

if __name__ == "__main__":
    print("Epson LQ-310 ESC/POS Printing")
    print("Creating receipt...")

    # Generate ESC/POS commands
    receipt_commands = create_receipt()

    # Send to printer
    print("Sending to printer...")
    if send_to_printer(receipt_commands):
        print("Print job sent successfully!")
    else:
        print("Failed to send print job")