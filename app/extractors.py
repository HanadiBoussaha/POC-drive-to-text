import io

import pdfplumber


class ExtractionError(Exception):
    """Raised when text cannot be extracted from a file."""


def extract_pdf_text(content: bytes) -> str:
    """Extract the text layer of a native PDF."""
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
    except Exception as exc:
        raise ExtractionError("Could not read the PDF.") from exc

    return "\n\n".join(pages).strip()