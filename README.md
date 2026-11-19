# Drive-to-Text

Small web app that takes a **public Google Drive folder link**, lists the PDFs and images it contains, and extracts their text with a PDF parser or OCR.

Proof of concept for the Dixpertia technical assessment (Ref. TA-2026-01).

## Features

- List the PDFs and images (PNG, JPG, JPEG) of a public Drive folder; other file types are ignored
- Select files one by one or with "Select all", with a live counter of selected files
- Per-file status: `pending`, `processing`, `done`, `failed`
- Native PDFs go through a PDF parser, images through OCR
- Scanned PDFs (no text layer) are detected and sent to OCR automatically
- A failing file never stops the rest of the batch
- OCR language choice (French + English, English, French, Arabic)
- Export of the results as JSON
- Clear errors for invalid or private links

## Tech stack

| Part | Choice | Why |
|---|---|---|
| Backend | FastAPI (Python) | Small, typed, easy to test |
| Drive access | Google Drive API v3 + API key | Reads public folders without user OAuth |
| PDF parsing | pdfplumber (MIT) | Permissive licence, used instead of PyMuPDF (AGPL-3.0) |
| OCR | Tesseract + pytesseract (Apache-2.0) | Open source, self-hosted, supports French, English and Arabic |
| Frontend | Plain HTML/CSS/JS, no build step | Nothing to install, easy to read |

## Prerequisites

- Python 3.10 or newer (tested on 3.12)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) with the French and Arabic language data
- A Google Drive API key (Google Cloud Console: enable "Google Drive API", then create an API key)

## Installation

```bash
git clone https://github.com/HanadiBoussaha/POC-drive-to-text.git
cd POC-drive-to-text
python -m venv .venv
.venv\Scripts\activate        # Windows (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

## Configuration

```bash
copy .env.example .env        # Linux/macOS: cp .env.example .env
```

Then edit `.env`:

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Your Google Drive API key (required) |
| `TESSERACT_CMD` | Path to the Tesseract executable. The line is commented out in `.env.example`: remove the leading `#` and set your path **only if** `tesseract` is not in your PATH (typical on Windows) |

The `.env` file is ignored by Git. Never commit your key.

## Run

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000, paste a public Drive folder link, click **List files**, select files, then **Validate**.

## Tests

```bash
pytest
```

Tests need neither the internet nor a Google key: Drive calls are replaced by fakes.

## Project structure

```
app/
  drive.py        Drive API: list and download files
  extractors.py   PDF parsing and OCR
  batch.py        Per-file processing, status and error isolation
  main.py         FastAPI routes
static/index.html Single-page UI
tests/            Unit and API tests
examples/         Sample JSON output
```

Each module has one responsibility: `extractors.py` knows nothing about Drive, and `batch.py` is the only place that chooses between parser and OCR.

## API

| Route | Description |
|---|---|
| `POST /api/files` | `{"url": "..."}` returns the PDFs and images of the folder |
| `POST /api/process` | Starts a background job for the selected files, returns a `job_id` |
| `GET /api/jobs/{id}` | Returns the status and text of each file |

## Sample output

See [`examples/sample_output.json`](examples/sample_output.json), produced from a test Drive folder containing fictional documents (native PDFs, images, a scanned PDF and a file type that is ignored).

## Licences

This project is released under the MIT licence (see `LICENSE`).
Third-party dependencies and their licences are listed in [`LICENSES.md`](LICENSES.md). PyMuPDF (AGPL-3.0) was deliberately avoided.

## Known limits

- Only **public** folders are supported (API key, no user OAuth).
- Subfolders are not scanned, and only the first 1000 files of a folder are listed (no pagination).
- Google Docs/Sheets and other file types are ignored.
- Jobs are stored in memory: they are lost when the server restarts, and files are processed one by one.
- OCR is never perfect: accuracy depends on image quality, resolution and language; tables are read as plain text.
- Files are loaded fully in memory, so very large files may be slow.
- Tesseract must be installed separately; without it, images and scanned PDFs fail with a clear message while native PDFs still work.
- No authentication on the app: it is meant to run locally.

## Possible improvements

- Process files in parallel and persist jobs in a database
- Scan subfolders and paginate the Drive listing
- Docker Compose setup (app + Tesseract)
- Extract tables from PDFs