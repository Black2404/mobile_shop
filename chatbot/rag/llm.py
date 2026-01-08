from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"), # Lấy key từ môi trường
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def ask_llm(prompt):
    try:
        res = client.chat.completions.create(
            model="gemini-2.5-flash",  
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        print(f"Lỗi gọi AI: {e}")
        return "Xin lỗi, tôi không thể kết nối với bộ não AI lúc này."