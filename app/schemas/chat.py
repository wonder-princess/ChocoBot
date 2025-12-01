from typing import List, Literal
from pydantic import BaseModel

RoleType = Literal["user", "assistant"]


class ChatMessage(BaseModel):
    role: RoleType
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    history: List[ChatMessage]
