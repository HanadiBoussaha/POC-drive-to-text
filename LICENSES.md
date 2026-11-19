# Third-party licenses

Main dependencies of this project, their licences, and whether they can be used in a closed-source commercial product.

| Dependency | Version | Licence | Commercial use | Note |
|---|---|---|---|---|
| fastapi | 0.163.1 | MIT | Yes | |
| uvicorn | 0.54.0 | BSD-3-Clause | Yes | |
| requests | 2.34.2 | Apache-2.0 | Yes | Keep NOTICE file if redistributed |
| python-dotenv | 1.2.4 | BSD-3-Clause | Yes | |
| pdfplumber | 0.11.10 | MIT | Yes | Chosen over PyMuPDF (AGPL-3.0) |
| pytest | 9.2.0 | MIT | Yes | Dev dependency only |
| pytesseract | 0.3.13 | Apache-2.0 | Yes | Python wrapper for Tesseract |
| Pillow | 13.0.0 | MIT-CMU (HPND) | Yes | Image loading |
| Tesseract OCR (external program) | 5.5.3 | Apache-2.0 | Yes | Installed separately, not bundled |
| httpx | 0.28.1 | BSD-3-Clause | Yes | Dev dependency only (API tests) |