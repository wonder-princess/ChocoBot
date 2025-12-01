from typing import List, Dict

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.core.chat_service import call_openai_chat

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    try:
        history_dicts: List[Dict[str, str]] = [
            {"role": m.role, "content": m.content} for m in payload.history
        ]
        ai_reply = call_openai_chat(history_dicts, payload.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

    new_history: List[ChatMessage] = payload.history + [
        ChatMessage(role="user", content=payload.message),
        ChatMessage(role="assistant", content=ai_reply),
    ]

    return ChatResponse(reply=ai_reply, history=new_history)
