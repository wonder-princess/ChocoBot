from fastapi import APIRouter
from app.schemas.duet import DuetRequest, DuetResponse, DuetTurn
from app.core.duet_service import run_duet_conversation

router = APIRouter(prefix="/api", tags=["duet"])


@router.post("/duet", response_model=DuetResponse)
async def duet_endpoint(payload: DuetRequest) -> DuetResponse:
    topic, turns_raw = run_duet_conversation(
        topic=payload.topic,
        max_turns_override=payload.max_turns,
    )

    turns = [DuetTurn(**t) for t in turns_raw]

    return DuetResponse(
        topic=topic,
        turns=turns,
    )
