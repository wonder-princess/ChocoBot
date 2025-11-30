from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from app.core.config import OPENAI_SETTINGS

load_dotenv()
_client = OpenAI()


def build_messages(history: List[Dict[str, str]], user_message: str):
    messages = [{"role": "system", "content": OPENAI_SETTINGS.system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages


def call_openai_chat(history: List[Dict[str, str]], user_message: str) -> str:
    messages = build_messages(history, user_message)

    response = _client.chat.completions.create(
        model=OPENAI_SETTINGS.model,
        messages=messages,
        temperature=OPENAI_SETTINGS.temperature,
        max_tokens=OPENAI_SETTINGS.max_tokens
    )

    return response.choices[0].message.content