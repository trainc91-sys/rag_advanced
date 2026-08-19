import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def main():
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token or hf_token == "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        print("[WARNING] Bạn chưa thay thế 'HF_TOKEN' thực tế trong file .env!")
        print("Vui lòng mở file .env và điền Token Hugging Face của bạn (ví dụ: HF_TOKEN=hf_abc123...)")
        return

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=hf_token,
    )

    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V4-Flash-0731:deepinfra",
        messages=[
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ],
    )

    print("Response from HF Router:")
    print(completion.choices[0].message.content)

if __name__ == "__main__":
    main()
