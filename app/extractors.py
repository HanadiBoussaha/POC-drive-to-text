import io
import os

import pdfplumber
import pytesseract
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

if os.getenv("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")

DEFAULT_OCR_LANG = "fra+eng"
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

def extract_image_text(content: bytes, lang: str = DEFAULT_OCR_LANG) -> str:
    """Extract text from an image with Tesseract OCR."""
    try:
        image = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(image, lang=lang)
    except pytesseract.TesseractNotFoundError as exc:
        raise ExtractionError("Tesseract is not installed or not found.") from exc
    except Exception as exc:
        raise ExtractionError("Could not run OCR on the image.") from exc

    return text.strip()