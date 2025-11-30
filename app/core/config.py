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


def load_openai_settings() -> OpenAISettings:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    o = raw["openai"]

    return OpenAISettings(
        model=o.get("model", "gpt-4o-mini"),
        temperature=o.get("temperature", 0.7),
        max_tokens=o.get("max_tokens", 512),
        system_prompt=o.get("system_prompt", "You are a helpful assistant.")
    )


OPENAI_SETTINGS = load_openai_settings()