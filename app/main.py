import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.batch import FileResult, process_file
from app.drive import DriveError, list_files

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Drive-to-Text POC")

# In-memory job store (enough for a POC; a real product would use a database)
JOBS: dict[str, list[FileResult]] = {}


class FolderRequest(BaseModel):
    url: str


class DriveFile(BaseModel):
    id: str
    name: str
    type: str
    size: int = 0


class ProcessRequest(BaseModel):
    files: list[DriveFile]
    lang: str = "fra+eng"


def run_job(job_id: str, lang: str) -> None:
    """Process every file of a job, one by one, updating its status."""
    for result in JOBS[job_id]:
        process_file(result, lang)


@app.post("/api/files")
def api_list_files(body: FolderRequest):
    try:
        return {"files": list_files(body.url)}
    except DriveError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/process")
def api_process(body: ProcessRequest, background_tasks: BackgroundTasks):
    if not body.files:
        raise HTTPException(status_code=400, detail="No file selected.")
    job_id = uuid.uuid4().hex
    JOBS[job_id] = [FileResult(id=f.id, name=f.name, type=f.type) for f in body.files]
    background_tasks.add_task(run_job, job_id, body.lang)
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def api_job(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found.")
    results = JOBS[job_id]
    finished = all(r.status in ("done", "failed") for r in results)
    return {"finished": finished, "results": [r.__dict__ for r in results]}


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")