import pytest
from fastapi.testclient import TestClient
import asyncio
from pathlib import Path
import aiohttp
import json
from PIL import Image
import io
import uvicorn
import multiprocessing
import time
from main import app


# Start server process
def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")


@pytest.fixture(scope="session")
def server():
    proc = multiprocessing.Process(target=run_server, daemon=True)
    proc.start()
    time.sleep(1)  # Give the server time to start
    yield
    proc.terminate()
    proc.join()


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def test_image():
    # Create a small test image
    img = Image.new("RGB", (100, 100), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    return img_byte_arr


@pytest.mark.asyncio
async def test_websocket_status_change(server, test_client, test_image):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("http://127.0.0.1:8000/ws") as ws:
            # Upload image using test_client
            files = {"file": ("test.jpg", test_image, "image/jpeg")}
            response = test_client.post("/images", files=files)
            assert response.status_code == 200
            job_data = response.json()
            job_id = job_data["job_id"]

            # Wait for and collect websocket messages
            messages = []
            try:
                # We expect to receive a status update message
                msg = await ws.receive_json(timeout=10.0)  # Increased timeout
                messages.append(msg)
            except asyncio.TimeoutError:
                pytest.fail("Timeout waiting for websocket message")

            # Verify messages
            assert len(messages) > 0
            final_message = messages[-1]
            assert final_message["job_id"] == job_id
            assert final_message["status"] == "completed"
            assert isinstance(final_message["count"], int)

            # Verify final status through REST API
            status_response = test_client.get(f"/images/{job_id}")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "completed"
            assert status_data["count"] == final_message["count"]
