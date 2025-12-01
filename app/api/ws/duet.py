# app/api/routes_duet.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.duet import DuetRequest, DuetResponse, DuetTurn
from app.core.duet_service import (
    run_duet_conversation,
    run_duet_conversation_stream,
)

router = APIRouter(prefix="/api", tags=["duet"])


@router.post("/duet", response_model=DuetResponse)
async def duet_endpoint(payload: DuetRequest) -> DuetResponse:
    topic, turns_raw = await run_duet_conversation(
        topic=payload.topic,
        max_turns_override=payload.max_turns,
    )
    turns = [DuetTurn(**t) for t in turns_raw]
    return DuetResponse(topic=topic, turns=turns)


# ★ 追加：1ターンごとに送る WebSocket
@router.websocket("/ws/duet")
async def duet_ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # 最初のメッセージで topic / max_turns を受け取る想定
        init_data = await websocket.receive_json()
        topic = init_data.get("topic")
        max_turns = init_data.get("max_turns")

        # テーマ情報だけ先に送る
        # クライアント側で「テーマ: ...」表示に使う
        await websocket.send_json(
            {
                "type": "meta",
                "topic": topic,
                "max_turns": max_turns,
            }
        )

        # ターンごとに WebSocket で送信
        async def send_turn(turn: dict) -> None:
            await websocket.send_json(
                {
                    "type": "turn",
                    "data": turn,
                }
            )

        await run_duet_conversation_stream(
            topic=topic,
            max_turns_override=max_turns,
            on_turn=send_turn,
        )

        # 全部終わった合図
        await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        # クライアントが切断した場合は静かに終了
        return
    except Exception as e:
        # 何かあればエラー通知（必要ならログも）
        await websocket.send_json({"type": "error", "message": str(e)})
        return
    finally:
        await websocket.close()
