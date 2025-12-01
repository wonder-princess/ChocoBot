from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any, AsyncIterator

import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

from app.core.config import OPENAI_SETTINGS

load_dotenv()
_client = AsyncOpenAI()


@dataclass
class BotProfile:
    name: str
    system_prompt: str


def _create_initial_history(bot: BotProfile) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": bot.system_prompt,
        }
    ]


async def _call_bot_async(bot: BotProfile, history: List[Dict[str, str]]) -> str:
    resp = await _client.chat.completions.create(
        model=OPENAI_SETTINGS.model,
        messages=history,
        temperature=OPENAI_SETTINGS.temperature,
        max_tokens=OPENAI_SETTINGS.max_tokens,
        frequency_penalty=OPENAI_SETTINGS.frequency_penalty,
        presence_penalty=OPENAI_SETTINGS.presence_penalty,
    )
    return resp.choices[0].message.content


def resolve_topic_and_turns(
    topic: Optional[str],
    max_turns_override: Optional[int],
) -> Tuple[str, int]:
    topic_text = (topic or "").strip()
    if topic_text:
        effective_topic = topic_text
    else:
        effective_topic = OPENAI_SETTINGS.topic or "自由に雑談してください。"

    if max_turns_override is not None:
        max_turns = max_turns_override
    else:
        max_turns = OPENAI_SETTINGS.max_turns or 3

    if max_turns < 1:
        max_turns = 1

    return effective_topic, max_turns


async def duet_turn_stream(
    effective_topic: str,
    max_turns: int,
) -> AsyncIterator[Dict[str, Any]]:
    bot_a = BotProfile(
        name="BotA",
        system_prompt=OPENAI_SETTINGS.bot_1_system_prompt,
    )
    bot_b = BotProfile(
        name="BotB",
        system_prompt=OPENAI_SETTINGS.bot_2_system_prompt,
    )

    history_a = _create_initial_history(bot_a)
    history_b = _create_initial_history(bot_b)

    history_a.append({"role": "user", "content": effective_topic})

    for turn in range(1, max_turns + 1):
        # BotA
        reply_a = await _call_bot_async(bot_a, history_a)
        yield {
            "turn": turn,
            "speaker": bot_a.name,
            "content": reply_a,
        }
        history_a.append({"role": "assistant", "content": reply_a})
        history_b.append({"role": "user", "content": reply_a})

        await asyncio.sleep(1.0)

        # BotB
        reply_b = await _call_bot_async(bot_b, history_b)
        yield {
            "turn": turn,
            "speaker": bot_b.name,
            "content": reply_b,
        }
        history_b.append({"role": "assistant", "content": reply_b})
        history_a.append({"role": "user", "content": reply_b})

        await asyncio.sleep(1.0)


async def run_duet_conversation(
    topic: Optional[str],
    max_turns_override: Optional[int] = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    effective_topic, max_turns = resolve_topic_and_turns(topic, max_turns_override)

    turns: List[Dict[str, Any]] = []
    async for item in duet_turn_stream(effective_topic, max_turns):
        turns.append(item)

    return effective_topic, turns
