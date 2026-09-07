import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    raise ValueError("ELEVENLABS_API_KEY is missing from .env")

client = ElevenLabs(api_key=api_key)

text = """
नमस्ते... मैं Aria हूँ।
आज तुम्हारा दिन कैसा रहा?
अगर तुम थक गए हो, तो थोड़ा आराम कर लो।
मैं यहीं हूँ, तुमसे बात करने के लिए।
"""

audio = client.text_to_speech.convert(
    text=text,
    voice_id="zzyrrX00vfq8JzvcccMi",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)

with open("aria_elevenlabs_test.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)

print("Audio generated successfully!")

os.startfile("aria_elevenlabs_test.mp3")