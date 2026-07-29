import json
import os
import shutil
from pathlib import Path
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.react_agent import ReactAgent
from rag.vector_store import VectorStoreService
from utils.file_handler import get_file_md5_hex
from utils.logger_handler import logger
from utils.path_tool import get_abs_path

app = FastAPI(title="RAG Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response models ──────────────────────────────────────────


class ChatRequest(BaseModel):
    query: str


class DocumentInfo(BaseModel):
    filename: str
    md5: str
    ingested: bool
    size_kb: float
    preview: str = ""


# ── Lazy singletons ────────────────────────────────────────────────────

_agent: ReactAgent | None = None
_vector_store: VectorStoreService | None = None


def get_agent() -> ReactAgent:
    global _agent
    if _agent is None:
        _agent = ReactAgent()
    return _agent


def get_vector_store() -> VectorStoreService:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store


def _read_preview(filepath: str, max_chars: int = 200) -> str:
    """读取 txt 文件前 max_chars 个字符作为预览."""
    if not filepath.endswith(".txt"):
        return ""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read(max_chars)
            if len(text) >= max_chars:
                text = text[:max_chars].rsplit(" ", 1)[0] + "…"
            return text
    except Exception:
        return ""


# ── SPA fallback ───────────────────────────────────────────────────────


@app.get("/")
async def serve_frontend():
    """Serve the React frontend."""
    index_path = get_abs_path("frontend/dist/index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not built. Run: cd frontend && npm run build"}


# ── API Endpoints ──────────────────────────────────────────────────────


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "rag-agent-api"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """SSE streaming chat endpoint."""

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            agent = get_agent()
            for chunk in agent.execute_stream(req.query):
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Chat stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document to the knowledge base."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = Path(file.filename).suffix.lower()
    if ext not in (".txt", ".pdf"):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    data_dir = get_abs_path("data")
    os.makedirs(data_dir, exist_ok=True)

    save_path = os.path.join(data_dir, file.filename)
    try:
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    try:
        vs = get_vector_store()
        vs.load_document()
        md5 = get_file_md5_hex(save_path)
        return {
            "status": "ok",
            "filename": file.filename,
            "md5": md5,
            "message": "Document uploaded and ingested successfully",
        }
    except Exception as e:
        logger.error(f"Failed to ingest document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {e}")


@app.get("/api/documents")
async def list_documents():
    """List all documents in the knowledge base with ingestion status."""
    data_dir = get_abs_path("data")
    if not os.path.isdir(data_dir):
        return {"documents": []}

    ingested_md5s: set[str] = set()
    md5_store_path = get_abs_path("md5.text")
    if os.path.exists(md5_store_path):
        with open(md5_store_path, "r", encoding="utf-8") as f:
            ingested_md5s = {line.strip() for line in f if line.strip()}

    documents: list[DocumentInfo] = []
    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        if not os.path.isfile(filepath):
            continue
        ext = Path(filename).suffix.lower()
        if ext not in (".txt", ".pdf"):
            continue
        md5 = get_file_md5_hex(filepath)
        size_kb = round(os.path.getsize(filepath) / 1024, 1)
        preview = _read_preview(filepath)
        documents.append(
            DocumentInfo(
                filename=filename,
                md5=md5 or "",
                ingested=md5 in ingested_md5s if md5 else False,
                size_kb=size_kb,
                preview=preview,
            )
        )

    return {"documents": sorted(documents, key=lambda d: d.filename)}


@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from the knowledge base."""
    filepath = os.path.join(get_abs_path("data"), filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        os.remove(filepath)
        logger.info(f"Deleted document: {filename}")
        return {"status": "ok", "message": f"Deleted {filename}"}
    except Exception as e:
        logger.error(f"Failed to delete document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete: {e}")


@app.post("/api/documents/reingest")
async def reingest_documents():
    """Re-ingest all documents in the data directory."""
    try:
        vs = get_vector_store()
        vs.load_document()
        return {"status": "ok", "message": "Re-ingestion completed"}
    except Exception as e:
        logger.error(f"Re-ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Re-ingestion failed: {e}")


# ── Static files (must be last) ────────────────────────────────────────

frontend_dist = get_abs_path("frontend/dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
