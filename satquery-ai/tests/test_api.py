import pytest
import httpx
from io import BytesIO
from PIL import Image
import numpy as np

def make_test_png_bytes():
    arr = (np.random.rand(64, 64, 3) * 255).astype(np.uint8)
    img = Image.fromarray(arr)
    bio = BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

@pytest.mark.asyncio
async def test_health_check(client: httpx.AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"

@pytest.mark.asyncio
async def test_system_info(client: httpx.AsyncClient):
    response = await client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert "app_version" in data
    assert "device" in data
    assert "cpu_count" in data

@pytest.mark.asyncio
async def test_get_models(client: httpx.AsyncClient):
    response = await client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(m["id"] == "remote_sensing_vqa" for m in data)

@pytest.mark.asyncio
async def test_upload_file(client: httpx.AsyncClient):
    png_bytes = make_test_png_bytes()
    files = [('files', ('test_scene.png', png_bytes, 'image/png'))]
    
    response = await client.post("/api/v1/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "file_ids" in data
    assert len(data["file_ids"]) > 0

@pytest.mark.asyncio
async def test_analyze_flow(client: httpx.AsyncClient):
    # 1. Upload valid image
    png_bytes = make_test_png_bytes()
    files = [('files', ('test_optic.png', png_bytes, 'image/png'))]
    upload_res = await client.post("/api/v1/upload", files=files)
    assert upload_res.status_code == 200
    fid = upload_res.json()["file_ids"][0]

    # 2. Analyze
    payload = {
        "query": "Describe the land cover and major objects in this scene",
        "file_ids": [fid],
        "input_mode": "single"
    }
    response = await client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert "answer" in data
    assert "task_type" in data
    assert "trace" in data
    assert len(data["trace"]) > 0
    assert "confidence" in data
