from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.core.chat_service import call_openai_chat

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    history_dicts = [m.model_dump() for m in payload.history]
    ai_reply = call_openai_chat(history_dicts, payload.message)

    new_history = payload.history + [
        ChatMessage(role="user", content=payload.message),
        ChatMessage(role="assistant", content=ai_reply),
    ]

    return ChatResponse(reply=ai_reply, history=new_history)
