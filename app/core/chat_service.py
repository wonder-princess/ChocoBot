from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

from app.core.config import OPENAI_SETTINGS

load_dotenv()
_client = OpenAI()


def build_messages(history: List[Dict[str, str]], user_message: str) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": OPENAI_SETTINGS.system_prompt}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages


def call_openai_chat(history: List[Dict[str, str]], user_message: str) -> str:
    messages = build_messages(history, user_message)

    response = _client.chat.completions.create(
        model=OPENAI_SETTINGS.model,
        messages=messages,
        temperature=OPENAI_SETTINGS.temperature,
        max_tokens=OPENAI_SETTINGS.max_tokens,
        frequency_penalty=OPENAI_SETTINGS.frequency_penalty,
        presence_penalty=OPENAI_SETTINGS.presence_penalty,
    )

    return response.choices[0].message.content
