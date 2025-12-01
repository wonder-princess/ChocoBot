from dataclasses import dataclass
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "ai_settings.json"


@dataclass
class OpenAISettings:
    model: str
    temperature: float
    max_tokens: int
    system_prompt: str
    frequency_penalty: float
    presence_penalty: float
    bot_1_system_prompt: str
    bot_2_system_prompt: str
    topic: str
    max_turns: int


def load_openai_settings() -> OpenAISettings:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    openai = raw.get("openai", {})
    bot_1 = raw.get("bot_1", {})
    bot_2 = raw.get("bot_2", {})
    setting_duet = raw.get("setting_duet", {})

    model = openai.get("model", "gpt-4o-mini")
    temperature = float(openai.get("temperature", 0.7))
    max_tokens = int(openai.get("max_tokens", 512))
    system_prompt = openai.get("system_prompt", "You are a helpful assistant.")
    frequency_penalty = float(openai.get("frequency_penalty", 0.0))
    presence_penalty = float(openai.get("presence_penalty", 0.0))

    bot_1_system_prompt = (bot_1.get("system_prompt") or "") + (bot_1.get("hobby") or "")
    bot_2_system_prompt = (bot_2.get("system_prompt") or "") + (bot_2.get("hobby") or "")

    topic = setting_duet.get("topic", "")
    max_turns = int(setting_duet.get("max_turns", 3))

    return OpenAISettings(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        bot_1_system_prompt=bot_1_system_prompt,
        bot_2_system_prompt=bot_2_system_prompt,
        topic=topic,
        max_turns=max_turns,
    )


OPENAI_SETTINGS = load_openai_settings()
