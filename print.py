# print.py - Windows printing script for Epson LQ-310 with 5-inch paper

import win32print
import win32api
import os
import tempfile

# Printer configuration
PRINTER_NAME = "EPSON-LQ-310"  # Must match exactly what's in Windows printers
PAPER_WIDTH = 5  # inches (used for formatting)
SAMPLE_TEXT = """This is a test print from Epson LQ-310

Company Name: YOUR COMPANY
Invoice No: TEST-12345
Date: {date}
--------------------------------
Item           Qty    Price
--------------------------------
Product 1        2     $10.00
Product 2        1     $15.50
Service Fee      1     $20.00
--------------------------------
Total:          $45.50
--------------------------------

Thank you for your business!
"""

def print_to_epson(text, copies=1, font_size=12):
    """
    Print text to Epson LQ-310 on Windows
    - text: The text to print
    - copies: Number of copies to print
    - font_size: Point size for the text (affects formatting)
    """
    try:
        # Get the default printer (or use the specified one)
        printer_name = win32print.GetDefaultPrinter()
        if PRINTER_NAME:
            printer_name = PRINTER_NAME

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write(text)
            temp_filename = f.name

        # Print using Windows' built-in print command
        for _ in range(copies):
            win32api.ShellExecute(
                0,
                "print",
                temp_filename,
                f'/d:"{printer_name}"',
                ".",
                0
            )

        # Wait a moment before deleting the temp file
        import time
        time.sleep(5)
        os.unlink(temp_filename)

        print(f"Successfully sent {copies} copy/copies to {printer_name}")
        return True

    except Exception as e:
        print(f"Error occurred while printing: {str(e)}")
        if 'temp_filename' in locals() and os.path.exists(temp_filename):
            os.unlink(temp_filename)
        return False

if __name__ == "__main__":
    from datetime import datetime

    print("EPSON LQ-310 Windows Printing Script")
    print("------------------------------------")

    # Customize the sample text with current date
    customized_text = SAMPLE_TEXT.format(date=datetime.now().strftime("%Y-%m-%d"))

    # Print configuration
    print(f"Printer: {PRINTER_NAME}")
    print(f"Paper width: {PAPER_WIDTH} inches")
    print("Printing sample document...")

    # Call the print function
    print_to_epson(customized_text, copies=1)

    print("Done. Check your printer.")