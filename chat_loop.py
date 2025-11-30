from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def main():
    # 会話の履歴（システムプロンプト＋ユーザー／アシスタントのメッセージ）
    messages = [
        {
            "role": "system",
            "content": (
                "あなたは日本語で丁寧かつ簡潔に回答するアシスタントです。"
                "専門的な内容の場合は、要点を箇条書きで整理してから説明してください。"
            ),
        }
    ]

    print("チャット開始（終了するには 'exit' と入力）")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("終了します。")
            break

        # ユーザー発言を履歴に追加
        messages.append({"role": "user", "content": user_input})

        # OpenAIに問い合わせ
        try:
            response = client.chat.completions.create(
                model="gpt-5.1-mini",
                messages=messages,
            )
        except Exception as e:
            print("Error:", e)
            continue

        assistant_message = response.choices[0].message.content
        print("Bot:", assistant_message)

        # モデルの返答も履歴に追加
        messages.append({"role": "assistant", "content": assistant_message})


if __name__ == "__main__":
    main()
