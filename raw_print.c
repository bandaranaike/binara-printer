#include <windows.h>
#include <stdio.h>  // For printf (console messages)
#include <stdlib.h> // For malloc, free
#include <string.h> // For strlen, memcpy

// --- Configuration ---
// IMPORTANT: Change this to the exact name of your printer in Windows
const char* G_PRINTER_NAME = "EPSON-LQ-310";

// Function to send raw data to the printer
void sendRawDataToPrinter(const char* szPrinterName, const BYTE* pData, DWORD dwDataSize) {
    HANDLE hPrinter = NULL;
    DOC_INFO_1A DocInfo; // Use DOC_INFO_1A for ANSI strings
    DWORD dwJob = 0;
    DWORD dwBytesWritten = 0;
    BOOL bStatus = FALSE;

    // 1. Open a handle to the printer.
    if (!OpenPrinterA((LPSTR)szPrinterName, &hPrinter, NULL)) {
        printf("Error: Failed to open printer '%s'. Error code: %lu\n", szPrinterName, GetLastError());
        return;
    }

    // 2. Fill in the DOC_INFO_1 structure.
    memset(&DocInfo, 0, sizeof(DocInfo));
    DocInfo.pDocName = (LPSTR)"C Raw Print Job";
    DocInfo.pOutputFile = NULL;
    DocInfo.pDatatype = (LPSTR)"RAW"; // Crucial: Specify RAW data type

    // 3. Notify the spooler that a document is beginning.
    dwJob = StartDocPrinterA(hPrinter, 1, (LPBYTE)&DocInfo);
    if (dwJob == 0) {
        printf("Error: Failed to start document. Error code: %lu\n", GetLastError());
        ClosePrinter(hPrinter);
        return;
    }

    // 4. Start a page.
    if (!StartPagePrinter(hPrinter)) {
        printf("Error: Failed to start page. Error code: %lu\n", GetLastError());
        EndDocPrinter(hPrinter);
        ClosePrinter(hPrinter);
        return;
    }

    // 5. Send the data to the printer.
    bStatus = WritePrinter(hPrinter, (LPVOID)pData, dwDataSize, &dwBytesWritten);
    if (!bStatus) {
        printf("Error: WritePrinter failed. Error code: %lu\n", GetLastError());
    } else if (dwBytesWritten != dwDataSize) {
        printf("Warning: Not all bytes were written. Sent: %lu, Written: %lu\n", dwDataSize, dwBytesWritten);
    } else {
        printf("Data successfully sent to printer (%lu bytes).\n", dwBytesWritten);
    }

    // 6. End the page.
    if (!EndPagePrinter(hPrinter)) {
        printf("Error: Failed to end page. Error code: %lu\n", GetLastError());
    }

    // 7. End the document.
    if (!EndDocPrinter(hPrinter)) {
        printf("Error: Failed to end document. Error code: %lu\n", GetLastError());
    }

    // 8. Close the printer handle.
    if (!ClosePrinter(hPrinter)) {
        printf("Error: Failed to close printer. Error code: %lu\n", GetLastError());
    }
}

int main() {
    // --- Define ESC/P Commands (as BYTE arrays) ---
    const BYTE CMD_INIT_PRINTER[]         = { 0x1B, '@' };                      // ESC @ (Initialize)
    const BYTE CMD_SET_LINE_SPACING_1_6[] = { 0x1B, '2' };                      // ESC 2 (Set line spacing to 1/6 inch)

    // For 5-inch paper at 6 Lines Per Inch (LPI) = 30 lines
    // Adjust PAGE_LENGTH_LINES if your LPI or desired paper height (in lines) differs.
    const BYTE PAGE_LENGTH_LINES          = 30;
    const BYTE CMD_SET_PAGE_LENGTH[]      = { 0x1B, 'C', PAGE_LENGTH_LINES };  // ESC C n (Set page length to n lines)

    const BYTE CMD_FORM_FEED[]            = { 0x0C };                           // Form Feed (eject page)

    // --- Prepare Text Data (your bill content) ---
    // Ensure text formatting (line breaks, spacing) fits your paper width.
    // For ASCII/simple text, char* is fine. For other encodings, ensure printer compatibility.
    const char* textBillData =
        "  Binara Medical Centre (C Example)\n"
        "  ---------------------------------\n"
        "  Bill No.: C-001      Date: 31/05/2025\n"
        "  Customer: Test Customer\n"
        "\n"
        "  Services:\n"
        "    Service Alpha   - Rs. 1000.00\n"
        "    Service Beta    - Rs.  500.00\n"
        "\n"
        "  Total:            Rs. 1500.00\n"
        "\n\n\n"; // Extra newlines for spacing before FF

    // --- Combine commands and text data into a single buffer ---
    DWORD textSize = strlen(textBillData);
    DWORD totalDataSize = sizeof(CMD_INIT_PRINTER) +
                          sizeof(CMD_SET_LINE_SPACING_1_6) +
                          sizeof(CMD_SET_PAGE_LENGTH) +
                          textSize +
                          sizeof(CMD_FORM_FEED);

    BYTE* printBuffer = (BYTE*)malloc(totalDataSize);
    if (printBuffer == NULL) {
        printf("Error: Failed to allocate memory for print buffer.\n");
        return 1;
    }

    BYTE* currentPos = printBuffer; // Pointer to fill the buffer

    memcpy(currentPos, CMD_INIT_PRINTER, sizeof(CMD_INIT_PRINTER));
    currentPos += sizeof(CMD_INIT_PRINTER);

    memcpy(currentPos, CMD_SET_LINE_SPACING_1_6, sizeof(CMD_SET_LINE_SPACING_1_6));
    currentPos += sizeof(CMD_SET_LINE_SPACING_1_6);

    memcpy(currentPos, CMD_SET_PAGE_LENGTH, sizeof(CMD_SET_PAGE_LENGTH));
    currentPos += sizeof(CMD_SET_PAGE_LENGTH);

    memcpy(currentPos, textBillData, textSize); // Copy text data
    currentPos += textSize;

    memcpy(currentPos, CMD_FORM_FEED, sizeof(CMD_FORM_FEED));

    // --- Send the combined data to the printer ---
    sendRawDataToPrinter(G_PRINTER_NAME, printBuffer, totalDataSize);

    free(printBuffer); // Clean up allocated memory

    return 0;
}