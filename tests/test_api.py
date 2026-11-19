from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_invalid_link_returns_clear_error():
    response = client.post("/api/files", json={"url": "not a drive link"})
    assert response.status_code == 400
    assert "Invalid" in response.json()["detail"]


def test_process_without_files_is_rejected():
    response = client.post("/api/process", json={"files": []})
    assert response.status_code == 400


def test_unknown_job_returns_404():
    assert client.get("/api/jobs/unknown").status_code == 404