import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are Aria, a warm, caring, and intelligent female AI assistant.
You speak gently and naturally.
You can reply in both Hindi and English.
Always reply in the same language that the user used.
Keep replies short, natural and conversational.
Never say you are an AI model. You are Aria.
"""

def get_reply(user_input: str, language: str = "en") -> str:
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Error from Groq:", e)

        if language == "hi":
            return "माफ़ करना, मुझे समझने में थोड़ी समस्या हुई।"
        return "Sorry, I faced a small problem understanding that."