from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes_chat import router as chat_router
from app.api.routes_duet import router as duet_router
from app.core.duet_service import resolve_topic_and_turns, duet_turn_stream

BASE_DIR = Path(__file__).resolve().parent
frontend_dir = BASE_DIR / "frontend"

app = FastAPI(title="ChocoBot")

app.include_router(chat_router)
app.include_router(duet_router)

app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def serve_front():
    return FileResponse(frontend_dir / "index.html")


@app.websocket("/ws/duet")
async def duet_ws(websocket: WebSocket):
    await websocket.accept()

    try:
        init = await websocket.receive_json()
    except WebSocketDisconnect:
        return
    except Exception:
        await websocket.close(code=1003)
        return

    topic = init.get("topic")
    max_turns = init.get("max_turns")
    effective_topic, resolved_max_turns = resolve_topic_and_turns(topic, max_turns)

    await websocket.send_json({"type": "meta", "topic": effective_topic})

    try:
        async for item in duet_turn_stream(effective_topic, resolved_max_turns):
            await websocket.send_json(
                {
                    "type": "turn",
                    "turn": item["turn"],
                    "speaker": item["speaker"],
                    "content": item["content"],
                }
            )

        await websocket.send_json({"type": "end"})
    except WebSocketDisconnect:
        return
    except Exception as e:
        try:
            await websocket.send_json(
                {"type": "error", "message": f"server error: {e}"}
            )
        finally:
            await websocket.close(code=1011)
