from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def chat_once(user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",   # ←ここを修正
        messages=[
            {"role": "system", "content": "あなたは日本語で丁寧に答えるアシスタントです。"},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    text = input("You: ")
    reply = chat_once(text)
    print("Bot:", reply)
