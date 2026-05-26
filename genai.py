import os
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
Question = input('請問要問AI什麼問題?')
response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=Question,
)

print(response.text)
