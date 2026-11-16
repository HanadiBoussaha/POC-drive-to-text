import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

DRIVE_API_URL = "https://www.googleapis.com/drive/v3/files"
ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpg",
}


class DriveError(Exception):
    """Raised when the Drive folder cannot be listed."""


def extract_folder_id(url: str) -> str:
    """Return the folder ID from a Google Drive folder URL."""
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise DriveError("Invalid Google Drive folder link.")
    return match.group(1)


def list_files(url: str) -> list[dict]:
    """List the PDFs and images of a public Drive folder."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise DriveError("GOOGLE_API_KEY is not configured.")

    folder_id = extract_folder_id(url)
    params = {
        "q": f"'{folder_id}' in parents and trashed = false",
        "fields": "files(id, name, mimeType, size)",
        "pageSize": 1000,
        "key": api_key,
    }
    response = requests.get(DRIVE_API_URL, params=params, timeout=15)

    if response.status_code in (403, 404):
        raise DriveError("Folder not found or not public.")
    if not response.ok:
        raise DriveError(f"Drive API error ({response.status_code}).")

    files = []
    for item in response.json().get("files", []):
        if item["mimeType"] in ALLOWED_MIME_TYPES:
            files.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "type": ALLOWED_MIME_TYPES[item["mimeType"]],
                    "size": int(item.get("size", 0)),
                }
            )
    return files

def download_file(file_id: str) -> bytes:
    """Download the raw content of a public Drive file."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise DriveError("GOOGLE_API_KEY is not configured.")

    response = requests.get(
        f"{DRIVE_API_URL}/{file_id}",
        params={"alt": "media", "key": api_key},
        timeout=60,
    )
    if not response.ok:
        raise DriveError(f"Could not download file ({response.status_code}).")
    return response.content