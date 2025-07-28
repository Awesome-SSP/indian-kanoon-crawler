### Objective:
Build an RPA bot that fetches PDF documents from a government portal or public utility API, extracts specific structured data (like case numbers, applicant names, or due amounts), and stores it securely in a database using credentials pulled from Vault.

---

## Tools Required:
requests or httpx – for API calls or web requests
pdfplumber or PyMuPDF – for PDF parsing
pyodbc / SQLAlchemy – for database access
keyring, Vault, or encrypted .json – for secrets
Optional: pandas, tabulate – for data presentation

---
## Workflow:
Get DB credentials securely
Fetch credentials from Vault or encrypted file.
Download public PDFs via HTTP
Example endpoint: https://example.gov/data/court/case_id=1234
Save PDFs with unique names locally.
Parse PDF files
Extract:
Case Number
Petitioner
Respondent
Hearing Date
Status
Store extracted data in DB
Using library to insert into SQL Server or SQLite.
Log summary
Keep a CSV or Excel file as an audit trail of what was fetched.