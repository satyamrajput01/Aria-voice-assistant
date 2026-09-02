import asyncio
from core.speech_to_text import listen
from core.text_to_speech import speak

def detect_language(text: str) -> str:
    """
    Very simple language detection.
    If text contains Hindi characters, treat it as Hindi.
    """
    for ch in text:
        if '\u0900' <= ch <= '\u097F':  # Hindi Unicode range
            return "hi"
    return "en"


async def main():
    print("Aria is ready...")

    while True:
        user_input = listen()

        if not user_input:
            continue

        language = detect_language(user_input)

        # Exit conditions
        if any(word in user_input for word in ["exit", "stop", "goodbye", "bye", "बंद", "बाय"]):
            if language == "hi":
                await speak("अलविदा। अपना ख्याल रखना।", language="hi")
            else:
                await speak("Goodbye. Take care.", language="en")
            break

        # Basic replies (temporary until we connect AI brain)
        if language == "hi":
            if any(word in user_input for word in ["नमस्ते", "हेलो", "ही"]):
                reply = "नमस्ते! मैं आर्या हूँ। मैं आपकी कैसे मदद कर सकती हूँ?"
            elif "नाम" in user_input:
                reply = "मेरा नाम आर्या है। मैं आपकी पर्सनल असिस्टेंट हूँ।"
            elif "कैसी हो" in user_input or "कैसे हो" in user_input:
                reply = "मैं ठीक हूँ, धन्यवाद। आप कैसे हो?"
            else:
                reply = "मैंने आपकी बात सुन ली है। मैं अभी भी सीख रही हूँ, लेकिन मैं यहाँ हूँ।"
        else:
            if any(word in user_input for word in ["hello", "hi", "hey"]):
                reply = "Hello! I'm Aria. How can I help you?"
            elif "your name" in user_input:
                reply = "My name is Aria. I'm your personal assistant."
            elif "how are you" in user_input:
                reply = "I'm doing well. Thank you for asking."
            else:
                reply = "I heard you. I am still learning, but I'm here with you."

        await speak(reply, language=language)


if __name__ == "__main__":
    asyncio.run(main())