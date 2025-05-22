from fastapi import (
    FastAPI,
    UploadFile,
    HTTPException,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Set
import shutil
import os
from pathlib import Path
import uuid
from datetime import datetime
import uvicorn
import asyncio

from db import get_db, Job, init_db
from detection import process_image

app = FastAPI()

# Create directories for storing images if they don't exist
UPLOAD_DIR = Path("uploads")
RESULT_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)


# ***Websocket***
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                self.disconnect(connection)


manager = ConnectionManager()


async def notify_status_change(job_id: str, status: str, count: int):
    await manager.broadcast({"job_id": job_id, "status": status, "count": count})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ***Websocket***


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.post("/images")
async def upload_image(file: UploadFile, db: AsyncSession = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Save the uploaded file
    input_path = UPLOAD_DIR / f"{job_id}_original.jpg"
    result_path = RESULT_DIR / f"{job_id}_result.jpg"

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create and save job to database
    job = Job(
        id=job_id,
        status="processing",
        count=0,
        img=str(input_path),
        created=datetime.now().astimezone(),
    )
    # Notify clients about processing
    await notify_status_change(job_id, "processing", 0)
    db.add(job)
    await db.commit()
    # try to async sleep here to simulate processing time of yolo
    await asyncio.sleep(1)

    try:
        count, boxes = await process_image(input_path, result_path)

        # Update job status and count
        job.status = "done"
        job.count = count
        await db.commit()

        # Notify clients about completion
        await notify_status_change(job_id, job.status, job.count)

    except Exception as e:
        # Update job status to error
        job.status = "error"
        await db.commit()
        await notify_status_change(job_id, job.status, job.count)
        raise HTTPException(status_code=500, detail=str(e))

    return {"job_id": job_id, "status": "done", "count": count}


@app.get("/images/{job_id}")
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"status": job.status, "count": job.count}


@app.get("/images/{job_id}/result.jpg")
async def get_result_image(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # if job.status != "completed":
    # raise HTTPException(status_code=400, detail="Image processing not completed")

    result_path = RESULT_DIR / f"{job_id}_result.jpg"
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="Result image not found")

    return FileResponse(str(result_path))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
