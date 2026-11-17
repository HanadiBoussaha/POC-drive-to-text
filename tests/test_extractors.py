import pytest

from app.extractors import ExtractionError, extract_pdf_text, extract_image_text


def test_invalid_pdf_raises_extraction_error():
    with pytest.raises(ExtractionError):
        extract_pdf_text(b"this is not a pdf")

def test_invalid_image_raises_extraction_error():
    with pytest.raises(ExtractionError):
        extract_image_text(b"this is not an image")

