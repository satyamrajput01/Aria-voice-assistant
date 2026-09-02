import edge_tts
import asyncio
import os

async def speak(text: str, emotion: str = "neutral"):
    """
    Aria speaks using a female neural voice.
    Emotion will later control speed and tone.
    """

    voice = "en-US-AriaNeural"   # Female voice

    # Adjust speaking rate based on emotion
    if emotion in ["sad", "tired", "dull"]:
        rate = "-15%"
    elif emotion in ["happy", "excited"]:
        rate = "+12%"
    else:
        rate = "+0%"

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate
    )

    await communicate.save("aria_output.mp3")

    # Play the audio (Windows)
    os.system("start aria_output.mp3")


# Test
if __name__ == "__main__":
    asyncio.run(speak("Hello, I am Aria. I'm here with you."))