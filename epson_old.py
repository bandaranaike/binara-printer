import win32print
import win32api

def print_with_epson():
    # Printer name
    printer_name = "EPSON LQ-300+ /II"

    # Open printer
    printer = win32print.OpenPrinter(printer_name)
    try:
        # Create a raw print job
        job = win32print.StartDocPrinter(printer, 1, ("Invoice", None, "RAW"))
        win32print.StartPagePrinter(printer)

        # Send ESC/P 2 commands (e.g., bold text, alignment)
        text = (
            "\x1B@"
            "Invoice\n\n"
            "Customer Name: John Doe\n"
            "Item A: $10.00\n"
            "Item B: $15.50\n"
            "Total: $25.50\n\n"
            "\x1B@"
        )
        win32print.WritePrinter(printer, text.encode("utf-8"))

        # End the print job
        win32print.EndPagePrinter(printer)
        win32print.EndDocPrinter(printer)
    finally:
        # Close the printer
        win32print.ClosePrinter(printer)

if __name__ == "__main__":
    print_with_epson()
