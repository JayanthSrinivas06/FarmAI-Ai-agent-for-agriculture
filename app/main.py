"""
RakiCrops AI – FastAPI Application Entry Point

Run with:
    uvicorn app.main:app --reload --port 8000
"""
# ── Load .env FIRST so all subsequent imports see the env vars ──────────────
from dotenv import load_dotenv
load_dotenv()   # reads Raki_crops/.env into os.environ

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api import api_router
from app.core.config import FRONTEND_DIR

app = FastAPI(
    title="RakiCrops AI",
    description="AI-powered crop recommendation and agriculture plan generator.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False,   # prevent 307 on routes without trailing slash
)

# ── Middleware ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes ─────────────────────────────────────────────────────────────
app.include_router(api_router)

# ── Frontend (static files) ────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/{path:path}", include_in_schema=False)
def serve_static(path: str):
    file_path = FRONTEND_DIR / path
    if file_path.is_file():
        return FileResponse(str(file_path))
    return FileResponse(str(FRONTEND_DIR / "index.html"))
