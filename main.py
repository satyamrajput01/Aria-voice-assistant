import asyncio
import re

from core.speech_to_text import listen
from core.text_to_speech import speak
from core.brain import get_reply
from core.emotion_detector import detect_emotion
from core.memory import save_memory


def detect_language(text: str) -> str:
    """
    Detect Hindi based on Devanagari characters.
    Otherwise use English.
    """

    for ch in text:
        if '\u0900' <= ch <= '\u097F':
            return "hi"

    return "en"


def clean_memory_value(value: str) -> str:
    """
    Clean common phrases that should not be stored
    as part of the actual memory value.
    """

    value = value.strip()

    patterns = [
        r",?\s*please remember( this| it)?\.?$",
        r",?\s*remember( this| it)?\.?$",
        r",?\s*do remember( this| it)?\.?$",
        r",?\s*yaad rakhna\.?$",
        r",?\s*yaad rakhna please\.?$",
        r",?\s*yaad rakhna isey\.?$",
    ]

    for pattern in patterns:
        value = re.sub(
            pattern,
            "",
            value,
            flags=re.IGNORECASE
        )

    return value.strip(" .,!?-")


def extract_name(value: str) -> str:
    """
    Extract only the person's name from a sentence.

    Examples:

    'Satyam' -> 'Satyam'

    'Satyam remember it' -> 'Satyam'

    'Satyam I am building Aria' -> 'Satyam'

    'Satyam and I am a student' -> 'Satyam'
    """

    value = clean_memory_value(value)

    stop_patterns = [
        r"\s+i am\b.*$",
        r"\s+i'm\b.*$",
        r"\s+im\b.*$",
        r"\s+i want\b.*$",
        r"\s+i like\b.*$",
        r"\s+i love\b.*$",
        r"\s+i enjoy\b.*$",
        r"\s+i live\b.*$",
        r"\s+i study\b.*$",
        r"\s+i am building\b.*$",
        r"\s+i'm building\b.*$",
        r"\s+remember\b.*$",
        r"\s+please remember\b.*$",
        r"\s+do remember\b.*$",
        r"\s+yaad rakhna\b.*$",
    ]

    for pattern in stop_patterns:
        value = re.sub(
            pattern,
            "",
            value,
            flags=re.IGNORECASE
        )

    value = value.strip(" .,!?-")

    words = value.split()

    if len(words) > 2:
        value = " ".join(words[:2])

    return value.strip()


def handle_memory(user_input: str):
    """
    Detect simple personal information and save it to memory.

    Returns:
        True  -> memory was saved
        False -> nothing was saved
    """

    text = user_input.strip()

    # --------------------------------------------------
    # NAME - ENGLISH
    # --------------------------------------------------

    name_patterns = [
        r"^my name is (.+)$",
        r"^i am (.+)$",
        r"^i'm (.+)$",
    ]

    # Words that clearly indicate that "I am ..."
    # is NOT a person's name.
    invalid_name_words = {
        "building",
        "making",
        "creating",
        "developing",
        "working",
        "studying",
        "learning",
        "trying",
        "going",
        "doing",
        "feeling",
        "thinking",
        "planning",
        "using",
        "testing",
        "coding",
        "programming",
        "playing",
        "watching",
        "eating",
        "drinking",
        "sleeping",
        "tired",
        "happy",
        "sad",
        "angry",
        "excited",
        "busy",
        "fine",
        "okay",
        "back",
        "student",
        "developer",
        "engineer",
        "boy",
        "girl",
        "person",
        "a",
        "an",
        "the",
    }

    for pattern in name_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            name = extract_name(match.group(1)).strip()

            if not name:
                continue

            words = name.split()

            first_word = words[0].lower()

            # Reject obvious non-name statements.
            if first_word in invalid_name_words:
                continue

            # A name should normally contain only alphabetic
            # words, with a maximum of two words.
            if len(words) > 2:
                continue

            if not all(
                re.fullmatch(r"[A-Za-z]+", word)
                for word in words
            ):
                continue

            save_memory(
                "personal",
                "name",
                name
            )

            print(f"Memory saved: name = {name}")
            return True

    # --------------------------------------------------
    # NAME - HINDI / HINGLISH
    # --------------------------------------------------

    hindi_name_patterns = [
        r"^mera naam (.+?) hai$",
        r"^mera naam (.+?) h$",
        r"^main (.+?) hoon$",
        r"^mai (.+?) hoon$",
    ]

    for pattern in hindi_name_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            name = extract_name(match.group(1)).strip()

            if not name:
                continue

            words = name.split()

            if len(words) > 2:
                continue

            if not all(
                re.fullmatch(r"[A-Za-z]+", word)
                for word in words
            ):
                continue

            save_memory(
                "personal",
                "name",
                name
            )

            print(f"Memory saved: name = {name}")
            return True

    # --------------------------------------------------
    # LIKES - ENGLISH
    # --------------------------------------------------

    like_patterns = [
        r"^i like (.+)$",
        r"^i really like (.+)$",
        r"^i enjoy (.+)$",
    ]

    for pattern in like_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            thing = clean_memory_value(
                match.group(1)
            )

            if thing:

                save_memory(
                    "preferences",
                    "likes",
                    thing
                )

                print(f"Memory saved: likes = {thing}")
                return True

    # --------------------------------------------------
    # LIKES - HINDI / HINGLISH
    # --------------------------------------------------

    hindi_like_patterns = [
        r"^mujhe (.+?) pasand hai$",
        r"^mujhe (.+?) pasand h$",
        r"^mujhe (.+?) bahut pasand hai$",
        r"^mujhe (.+?) bohot pasand hai$",
    ]

    for pattern in hindi_like_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            thing = clean_memory_value(
                match.group(1)
            )

            if thing:

                save_memory(
                    "preferences",
                    "likes",
                    thing
                )

                print(f"Memory saved: likes = {thing}")
                return True

    # --------------------------------------------------
    # LOVE - ENGLISH
    # --------------------------------------------------

    love_patterns = [
        r"^i love (.+)$",
        r"^i really love (.+)$",
    ]

    for pattern in love_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            thing = clean_memory_value(
                match.group(1)
            )

            if thing:

                save_memory(
                    "preferences",
                    "loves",
                    thing
                )

                print(f"Memory saved: loves = {thing}")
                return True

    # --------------------------------------------------
    # FAVORITES - ENGLISH
    # --------------------------------------------------

    favorite_match = re.match(
        r"^my favorite (.+?) is (.+)$",
        text,
        flags=re.IGNORECASE
    )

    if favorite_match:

        category = favorite_match.group(1).strip()

        value = clean_memory_value(
            favorite_match.group(2)
        )

        if category and value:

            save_memory(
                "preferences",
                f"favorite_{category.lower()}",
                value
            )

            print(
                f"Memory saved: favorite {category} = {value}"
            )

            return True

    # --------------------------------------------------
    # FAVORITES - HINGLISH
    # --------------------------------------------------

    hindi_favorite_patterns = [
        r"^meri favorite (.+?) (.+?) hai$",
        r"^mera favorite (.+?) (.+?) hai$",
    ]

    for pattern in hindi_favorite_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            category = match.group(1).strip()

            value = clean_memory_value(
                match.group(2)
            )

            if category and value:

                save_memory(
                    "preferences",
                    f"favorite_{category.lower()}",
                    value
                )

                print(
                    f"Memory saved: favorite {category} = {value}"
                )

                return True

    return False


def is_exit_command(user_input: str) -> bool:
    """
    Detect actual exit commands without accidentally
    treating words like 'buy' as 'bye'.
    """

    normalized = user_input.lower().strip()

    normalized = re.sub(
        r"[^\w\s]",
        "",
        normalized
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    )

    exit_commands = {
        "exit",
        "stop",
        "goodbye",
        "bye",
        "quit",
        "बंद",
        "बाय",
        "अलविदा",
    }

    if normalized in exit_commands:
        return True

    # Handles:
    # b y e
    if normalized.replace(" ", "") == "bye":
        return True

    return False


async def main():

    print("=" * 50)
    print("        ARIA - AI COMPANION")
    print("=" * 50)
    print("Aria is ready...")
    print("Speak to her. Say 'bye' to exit.")
    print()

    while True:

        try:
            user_input = listen()

        except KeyboardInterrupt:
            print()
            print("Aria stopped.")
            break

        except OSError as e:
            print()
            print(f"Microphone error: {e}")
            print("Restarting microphone...")
            continue

        if not user_input:
            continue

        # ----------------------------------------------
        # MEMORY
        # ----------------------------------------------

        handle_memory(user_input)

        # ----------------------------------------------
        # LANGUAGE
        # ----------------------------------------------

        language = detect_language(user_input)

        # ----------------------------------------------
        # EMOTION
        # ----------------------------------------------

        emotion, confidence = detect_emotion(user_input)

        print(f"Emotion: {emotion}")
        print(f"Confidence: {confidence:.2f}")

        # ----------------------------------------------
        # EXIT
        # ----------------------------------------------

        if is_exit_command(user_input):

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

        # ----------------------------------------------
        # ARIA BRAIN
        # ----------------------------------------------

        reply = get_reply(
            user_input=user_input,
            emotion=emotion,
            confidence=confidence,
            language=language
        )

        print(f"Aria: {reply}")
        print()

        # ----------------------------------------------
        # ARIA VOICE
        # ----------------------------------------------

        await speak(
            reply,
            language=language,
            emotion=emotion
        )


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print()
        print("Aria stopped.")