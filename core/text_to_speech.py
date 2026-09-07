import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    raise ValueError("ELEVENLABS_API_KEY is missing from .env")

client = ElevenLabs(api_key=api_key)

VOICE_ID = "zzyrrX00vfq8JzvcccMi"


async def speak(text: str, language: str = "en", emotion: str = "neutral"):
    try:
        # Adjust speaking speed based on emotion
        if emotion in ["sad", "tired"]:
            speed = 0.90
        elif emotion in ["happy", "excited"]:
            speed = 1.08
        elif emotion == "angry":
            speed = 0.95
        else:
            speed = 1.0

        audio = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.45,
                "similarity_boost": 0.80,
                "style": 0.35,
                "use_speaker_boost": True,
                "speed": speed,
            },
        )

        filename = "aria_output.mp3"

        with open(filename, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        os.startfile(filename)

    except Exception as e:
        print("ElevenLabs TTS error:", e)