import asyncio
from core.speech_to_text import listen
from core.text_to_speech import speak
from core.brain import get_reply

def detect_language(text: str) -> str:
    for ch in text:
        if '\u0900' <= ch <= '\u097F':
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

        # Get intelligent reply from Gemini
        reply = get_reply(user_input, language)

        await speak(reply, language=language)


if __name__ == "__main__":
    asyncio.run(main())