from typing import List, Literal, Optional
from pydantic import BaseModel

SpeakerType = Literal["BotA", "BotB"]


class DuetTurn(BaseModel):
    turn: int
    speaker: SpeakerType
    content: str


class DuetRequest(BaseModel):
    topic: Optional[str] = None
    max_turns: Optional[int] = None


class DuetResponse(BaseModel):
    topic: str
    turns: List[DuetTurn]
