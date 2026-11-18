Use the microsoft-office skill to create a new Excel invoice using my existing template.

**Original template:**
`/opt/data/invoices/templates/invoice_template.xlsx`

**New invoice details:**

Company information (A4):
- Company: Flint Enterprises
- Address: Tokyo, Japan
- Email: billing@example.com

Customer information (D4):
- Customer: ABC Corporation
- Address: Tokyo, Japan
- Email: accounts@example.com

Invoice details:
- Invoice Number (B8): INV-2026-11-001
- Invoice Date (E8): November 17, 2026
- Due Date (B9): November 30, 2026

Invoice items:

Item 1:
- Description (B12): Monthly IT Support
- Quantity (C12): 1
- Unit Price (D12): 50000

Payment instructions (A28):
- TEST INVOICE — DO NOT PAY.
- Thank you for your business.

**Instructions:**

1. Load the original Excel template.
2. Create a separate copy of the workbook.
3. Edit only the specified cells in the new copy.
4. Preserve the original workbook's formatting, merged cells, borders, fonts, and worksheet structure.
5. Preserve all formulas in cells E12:E23 and E25.
6. Keep the "How to use" worksheet unchanged.
7. Store invoice dates as Excel dates, not text.
8. Preserve the existing number formats.
9. Leave unused invoice item rows empty.
10. Save the completed invoice to:

`/opt/data/invoices/output/Invoice_TEST_2026-11.xlsx`

**Verification:**

After saving:
1. Open the newly created Excel file.
2. Verify that every supplied value was inserted correctly.
3. Confirm that all original formulas remain intact.
4. Verify that the workbook still contains both worksheets.
5. Confirm that the original template was not modified.
6. Report any formatting changes or unsupported features.

Do not overwrite the original invoice template.

Use the microsoft-office Excel tools and the existing Python environment.