import asyncio

from core.speech_to_text import listen
from core.text_to_speech import speak
from core.brain import get_reply
from core.emotion_detector import detect_emotion


def detect_language(text: str) -> str:
    """
    Detect Hindi based on Devanagari characters.
    Otherwise use English.
    """

    for ch in text:
        if '\u0900' <= ch <= '\u097F':
            return "hi"

    return "en"


async def main():

    print("=" * 50)
    print("        ARIA - AI COMPANION")
    print("=" * 50)
    print("Aria is ready...")
    print("Speak to her. Say 'bye' to exit.")
    print()

    while True:

        user_input = listen()

        if not user_input:
            continue

        language = detect_language(user_input)

        # Detect emotion
        emotion, confidence = detect_emotion(user_input)

        print(f"Emotion: {emotion}")
        print(f"Confidence: {confidence:.2f}")

        # Exit conditions
        exit_words = [
            "exit",
            "stop",
            "goodbye",
            "bye",
            "बंद",
            "बाय",
            "अलविदा"
        ]

        if any(word in user_input for word in exit_words):

            if language == "hi":
                await speak(
                    "अलविदा। अपना ख्याल रखना।",
                    language="hi",
                    emotion="neutral"
                )
            else:
                await speak(
                    "Goodbye. Take care.",
                    language="en",
                    emotion="neutral"
                )

            break

        # Get emotionally aware response
        reply = get_reply(
            user_input=user_input,
            emotion=emotion,
            confidence=confidence,
            language=language
        )

        print(f"Aria: {reply}")
        print()

        # Speak response using detected emotion
        await speak(
            reply,
            language=language,
            emotion=emotion
        )


if __name__ == "__main__":
    asyncio.run(main())