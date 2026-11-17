from app import batch


def test_failed_file_does_not_stop_the_batch(monkeypatch):
    def fake_download(file_id):
        if file_id == "bad":
            raise batch.DriveError("boom")
        return b"not a pdf"

    monkeypatch.setattr(batch, "download_file", fake_download)
    monkeypatch.setattr(batch, "extract_pdf_text", lambda content: "hello")

    files = [
        {"id": "bad", "name": "bad.pdf", "type": "pdf"},
        {"id": "ok", "name": "ok.pdf", "type": "pdf"},
    ]
    results = batch.process_batch(files)

    assert results[0].status == "failed"
    assert results[0].error == "boom"
    assert results[1].status == "done"
    assert results[1].text == "hello"


def test_empty_pdf_falls_back_to_ocr(monkeypatch):
    monkeypatch.setattr(batch, "download_file", lambda file_id: b"x")
    monkeypatch.setattr(batch, "extract_pdf_text", lambda content: "")
    monkeypatch.setattr(batch, "extract_scanned_pdf_text", lambda content, lang: "scanned text")

    result = batch.process_batch([{"id": "1", "name": "scan.pdf", "type": "pdf"}])[0]

    assert result.status == "done"
    assert result.method == "ocr_fallback"
    assert result.text == "scanned text"


def test_image_is_sent_to_ocr(monkeypatch):
    monkeypatch.setattr(batch, "download_file", lambda file_id: b"x")
    monkeypatch.setattr(batch, "extract_image_text", lambda content, lang: "ocr text")

    result = batch.process_batch([{"id": "1", "name": "a.png", "type": "png"}])[0]

    assert result.method == "ocr"
    assert result.text == "ocr text"