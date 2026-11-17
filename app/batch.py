from dataclasses import dataclass, field
from typing import Callable

from app.drive import DriveError, download_file
from app.extractors import (
    ExtractionError,
    extract_image_text,
    extract_pdf_text,
    extract_scanned_pdf_text,
)


@dataclass
class FileResult:
    id: str
    name: str
    type: str
    status: str = "pending"  # pending | processing | done | failed
    method: str | None = None  # pdf_parser | ocr | ocr_fallback
    text: str = ""
    error: str | None = None


def process_file(result: FileResult, lang: str = "fra+eng") -> FileResult:
    """Process one file. Never raises: errors are stored in the result."""
    result.status = "processing"
    try:
        content = download_file(result.id)

        if result.type == "pdf":
            text = extract_pdf_text(content)
            result.method = "pdf_parser"
            if not text:  # no text layer: probably a scan
                text = extract_scanned_pdf_text(content, lang)
                result.method = "ocr_fallback"
        else:
            text = extract_image_text(content, lang)
            result.method = "ocr"

        result.text = text
        result.status = "done"
    except (DriveError, ExtractionError) as exc:
        result.status = "failed"
        result.error = str(exc)
    except Exception as exc:  # safety net: one file must never stop the batch
        result.status = "failed"
        result.error = f"Unexpected error: {exc}"
    return result


def process_batch(
    files: list[dict],
    lang: str = "fra+eng",
    on_update: Callable[[FileResult], None] | None = None,
) -> list[FileResult]:
    """Process several files one by one. A failure never stops the others."""
    results = [FileResult(id=f["id"], name=f["name"], type=f["type"]) for f in files]
    for result in results:
        process_file(result, lang)
        if on_update:
            on_update(result)
    return results