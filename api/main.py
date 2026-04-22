from pathlib import Path
import logging
import logging.config
import tempfile
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from api.routers import projects, ai
from api.routers import a2ui
from api.routers import toolpath

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="AICAM API", version="1.0.0")

# Configure logging to file and console (log file placed in project root)
try:
    log_path = BASE_DIR / "skera_api.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": "INFO",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "level": "INFO",
                    "filename": str(log_path),
                    "mode": "a",
                },
            },
            "root": {"handlers": ["console", "file"], "level": "INFO"},
        }
    )
except Exception:
    logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(ai.router)
app.include_router(a2ui.router)
app.include_router(toolpath.router)
app.include_router(projects.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(a2ui.router, prefix="/api")
app.include_router(toolpath.router, prefix="/api")

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = BASE_DIR / "dist"
INDEX_FILE = DIST_DIR / "index.html"

@app.get("/", include_in_schema=False)
async def serve_root():
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    return {"message": "Welcome to AICAM API"}

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    asset_path = DIST_DIR / full_path
    if asset_path.exists() and asset_path.is_file():
        return FileResponse(asset_path)
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
