from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes_chat import router as chat_router
from app.api.routes_duet import router as duet_router

BASE_DIR = Path(__file__).resolve().parent
frontend_dir = BASE_DIR / "frontend"

app = FastAPI(title="ChocoBot")

app.include_router(chat_router)
app.include_router(duet_router)

app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def serve_front():
    return FileResponse(frontend_dir / "index.html")
