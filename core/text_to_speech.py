import edge_tts
import asyncio
import os

async def speak(text: str, language: str = "en", emotion: str = "neutral"):
    """
    Aria speaks in English or Hindi with female voice.
    """

    # Choose voice based on language
    if language == "hi":
        voice = "hi-IN-SwaraNeural"   # Female Hindi voice
    else:
        voice = "en-US-AriaNeural"    # Female English voice

    # Adjust speed based on emotion
    if emotion in ["sad", "tired", "dull"]:
        rate = "-15%"
    elif emotion in ["happy", "excited"]:
        rate = "+10%"
    else:
        rate = "+0%"

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate
    )

    await communicate.save("aria_output.mp3")
    os.system("start aria_output.mp3")


# Test
if __name__ == "__main__":
    asyncio.run(speak("नमस्ते, मैं आर्या हूँ।", language="hi"))