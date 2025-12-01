from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any

from dotenv import load_dotenv
from openai import OpenAI

from app.core.config import OPENAI_SETTINGS

load_dotenv()
_client = OpenAI()


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


def _call_bot(bot: BotProfile, history: List[Dict[str, str]]) -> str:
    response = _client.chat.completions.create(
        model=OPENAI_SETTINGS.model,
        messages=history,
        temperature=OPENAI_SETTINGS.temperature,
        max_tokens=OPENAI_SETTINGS.max_tokens,
        frequency_penalty=OPENAI_SETTINGS.frequency_penalty,
        presence_penalty=OPENAI_SETTINGS.presence_penalty,
    )
    return response.choices[0].message.content


def run_duet_conversation(
    topic: Optional[str],
    max_turns_override: Optional[int] = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    # 画面入力 → 設定 → デフォルト の順で topic を決定
    topic_text = (topic or "").strip()
    if topic_text:
        effective_topic = topic_text
    else:
        effective_topic = OPENAI_SETTINGS.topic or "自由に雑談してください。"

    # max_turns は引数優先、それ以外は設定ファイル
    if max_turns_override is not None:
        max_turns = max_turns_override
    else:
        max_turns = OPENAI_SETTINGS.max_turns or 3

    if max_turns < 1:
        max_turns = 1

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

    # 最初の一言を BotA に渡す
    history_a.append({"role": "user", "content": effective_topic})

    turns: List[Dict[str, Any]] = []

    for turn in range(1, max_turns + 1):
        # BotA
        reply_a = _call_bot(bot_a, history_a)
        turns.append(
            {
                "turn": turn,
                "speaker": bot_a.name,
                "content": reply_a,
            }
        )
        history_a.append({"role": "assistant", "content": reply_a})
        history_b.append({"role": "user", "content": reply_a})

        # BotB
        reply_b = _call_bot(bot_b, history_b)
        turns.append(
            {
                "turn": turn,
                "speaker": bot_b.name,
                "content": reply_b,
            }
        )
        history_b.append({"role": "assistant", "content": reply_b})
        history_a.append({"role": "user", "content": reply_b})

    return effective_topic, turns
