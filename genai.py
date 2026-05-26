import os
from google import genai

# 讀取環境變數
api_key = os.getenv("GEMINI_API_KEY")

# 建立 Gemini Client
client = genai.Client(api_key=api_key)

Question = input("請問要問AI什麼問題？")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=Question
)

print(response.text)
