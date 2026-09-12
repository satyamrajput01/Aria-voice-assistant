import asyncio
import re

from core.speech_to_text import listen
from core.text_to_speech import speak
from core.brain import get_reply
from core.memory import save_memory


# ==========================================================
# LANGUAGE DETECTION
# ==========================================================

def detect_language(text: str) -> str:
    """
    Detect Hindi, English, and Romanized Hindi/Hinglish.

    Supports:
    - Hindi written in Devanagari
    - Romanized Hindi
    - Hinglish
    - English
    - English words returned by STT in Devanagari
    """

    text = text.strip()

    if not text:
        return "en"

    text_lower = text.lower()

    # ------------------------------------------------------
    # COMMON ENGLISH WORDS
    # ------------------------------------------------------

    english_words = {
        "i", "me", "my", "you", "your", "we", "our",
        "they", "he", "she", "it", "this", "that",

        "am", "is", "are", "was", "were",
        "have", "has", "had",
        "do", "does", "did",
        "can", "could", "would", "should",

        "very", "really", "extremely", "little", "bit",

        "good", "great", "bad", "fine", "okay", "better",
        "best", "worst",

        "feel", "feeling", "felt",
        "love", "like", "want", "need",
        "talk", "speak", "listen", "help",

        "today", "tomorrow", "yesterday",
        "going", "everything", "nothing", "something",

        "tell", "give", "show", "what", "why",
        "how", "when", "where", "who",

        "hello", "hey", "hi",
        "please", "thanks", "thank",
        "joke", "funny",

        "computer", "phone", "laptop",
        "code", "coding", "project",
    }

    # ------------------------------------------------------
    # ROMANIZED HINDI / HINGLISH
    # ------------------------------------------------------

    hindi_words = {
        # Pronouns
        "main", "mai", "mein",
        "mujhe", "mujh", "mujhse",
        "mera", "meri", "mere",
        "hum", "ham",
        "humara", "hamara",
        "humari", "hamari",
        "tum", "tumhe", "tumse",
        "tumhara", "tumhari", "tumhare",
        "aap", "aapko", "aapka", "aapki", "aapke",

        # Helping verbs
        "hai", "hain", "ho", "hun", "hoon",
        "tha", "thi", "the",

        # Verbs
        "raha", "rahi", "rahe",
        "kar", "karke", "karna", "karne",
        "karo", "karte", "karti",
        "kiya", "kiye",
        "gaya", "gayi", "gaye",
        "aa", "aana", "aaya", "aayi",
        "jaa", "jana", "jane", "jao", "jaana",
        "de", "dena", "diya", "do",
        "lelo", "lena", "liya",
        "bata", "batao", "batana",
        "bol", "bolo",
        "sun", "suno",
        "dekh", "dekho",
        "dikha", "dikhao",

        # Common Hindi
        "aaj", "kal", "abhi",
        "bahut", "bohot",
        "achcha", "achha", "accha", "acha",
        "bura", "kya", "kyu", "kyun",
        "kaise", "kaisa", "kaisi",
        "kab", "kahan", "kahaan", "kaun",
        "kyon", "kyunki", "kyonki",
        "nahi", "nahin", "haan",
        "yaar", "bhai", "dost",
        "baat", "baatein", "baatain",
        "kuch", "kuchh",
        "sab", "sabhi", "sirf",
        "phir", "fir",
        "ab", "toh", "to", "bhi",
        "hi", "aur", "lekin", "magar",
        "isliye", "agar", "jab", "jabki",
        "jo", "yeh", "ye",
        "woh", "vo",
        "iska", "iski", "uska", "uski",

        # General conversation
        "chahiye",
        "chahta", "chahti", "chahte",
        "sakta", "sakti", "sakte",
        "pata", "malum", "maalum",
        "samajh", "samjha", "samjhi",
        "samajhta", "samajhti",
        "lag", "lagta", "lagti", "laga",
        "rakh", "rakhna", "rakho",
        "yaad", "bhool", "bhul",

        # Daily life
        "time", "din", "raat",
        "subah", "shaam",
        "ghar", "college",
        "padhai", "padhta", "padhti",
        "student", "log", "insaan",
    }

    # ------------------------------------------------------
    # NORMAL ROMANIZED TEXT ANALYSIS
    # ------------------------------------------------------

    words = re.findall(
        r"[a-zA-Z]+",
        text_lower
    )

    hindi_matches = sum(
        1
        for word in words
        if word in hindi_words
    )

    english_matches = sum(
        1
        for word in words
        if word in english_words
    )

    total_words = len(words)

    # Clear Romanized Hindi / Hinglish
    if hindi_matches >= 2:
        return "hi"

    # Short Hindi phrase
    if total_words <= 3 and hindi_matches >= 1:
        return "hi"

    # Clear English
    if english_matches >= 1 and hindi_matches == 0:
        return "en"

    # ------------------------------------------------------
    # DEVANAGARI ANALYSIS
    # ------------------------------------------------------

    has_devanagari = any(
        "\u0900" <= ch <= "\u097F"
        for ch in text
    )

    if has_devanagari:

        # --------------------------------------------------
        # English words that Google may return in
        # Devanagari phonetic form.
        # --------------------------------------------------

        devanagari_english = {
            "वेरी",
            "ग्रेट",
            "गुड",
            "बैड",
            "फाइन",
            "ओके",

            "गोइंग",
            "टुडे",
            "टुमॉरो",
            "एवरीथिंग",
            "नथिंग",
            "समथिंग",

            "रीयली",
            "रियली",

            "आई",
            "यू",
            "मी",
            "माय",
            "योर",
            "वी",

            "कैन",
            "कुड",
            "वुड",
            "शुड",

            "टेल",
            "टॉक",
            "स्पीक",
            "लिसन",
            "जोक",
            "हेल्प",

            "हैव",
            "हैज़",
            "एम",
            "इज़",
            "आर",

            "फील",
            "फीलिंग",
            "लव",
            "लाइक",
            "वांट",
            "नीड",

            "व्हाट",
            "व्हाय",
            "हाउ",
            "व्हेन",
            "वेयर",
            "हू",
        }

        devanagari_words = text.split()

        phonetic_english_matches = sum(
            1
            for word in devanagari_words
            if word.strip(".,!?।") in devanagari_english
        )

        if phonetic_english_matches >= 1:
            return "en"

        return "hi"

    # ------------------------------------------------------
    # DEFAULT
    # ------------------------------------------------------

    return "en"


# ==========================================================
# MEMORY HELPERS
# ==========================================================

def clean_memory_value(value: str) -> str:

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


# ==========================================================
# MEMORY HANDLER
# ==========================================================

def handle_memory(user_input: str):

    text = user_input.strip()

    # ------------------------------------------------------
    # NAME - ENGLISH
    # ------------------------------------------------------

    name_patterns = [
        r"^my name is (.+)$",
        r"^i'm called (.+)$",
    ]

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
        "really",
    }

    for pattern in name_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            name = extract_name(
                match.group(1)
            ).strip()

            if not name:
                continue

            words = name.split()

            if not words:
                continue

            first_word = words[0].lower()

            if first_word in invalid_name_words:
                continue

            if len(words) > 2:
                continue

            if not all(
                re.fullmatch(
                    r"[A-Za-z]+",
                    word
                )
                for word in words
            ):
                continue

            save_memory(
                "personal",
                "name",
                name
            )

            print(
                f"Memory saved: name = {name}"
            )

            return True

    # ------------------------------------------------------
    # NAME - HINDI / HINGLISH
    # ------------------------------------------------------

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

            name = extract_name(
                match.group(1)
            ).strip()

            if not name:
                continue

            words = name.split()

            if len(words) > 2:
                continue

            if not all(
                re.fullmatch(
                    r"[A-Za-z]+",
                    word
                )
                for word in words
            ):
                continue

            save_memory(
                "personal",
                "name",
                name
            )

            print(
                f"Memory saved: name = {name}"
            )

            return True

    # ------------------------------------------------------
    # LIKES - ENGLISH
    # ------------------------------------------------------

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

                print(
                    f"Memory saved: likes = {thing}"
                )

                return True

    # ------------------------------------------------------
    # LIKES - HINDI / HINGLISH
    # ------------------------------------------------------

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

                print(
                    f"Memory saved: likes = {thing}"
                )

                return True

    # ------------------------------------------------------
    # LOVE - ENGLISH
    # ------------------------------------------------------

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

                print(
                    f"Memory saved: loves = {thing}"
                )

                return True

    # ------------------------------------------------------
    # FAVORITES - ENGLISH
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # FAVORITES - HINGLISH
    # ------------------------------------------------------

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


# ==========================================================
# EXIT COMMAND
# ==========================================================

def is_exit_command(user_input: str) -> bool:

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

    if normalized.replace(" ", "") == "bye":
        return True

    return False


# ==========================================================
# MAIN
# ==========================================================

async def main():

    print("=" * 50)
    print("        ARIA - AI COMPANION")
    print("=" * 50)
    print("Aria is ready...")
    print("Speak to her. Say 'bye' to exit.")
    print()

    while True:

        try:

            # ----------------------------------------------
            # LISTEN
            # ----------------------------------------------

            result = listen()

            if not result:
                continue

            user_input, audio_data = result

            if not user_input:
                continue

        except KeyboardInterrupt:

            print()
            print("Aria stopped.")
            break

        except OSError as e:

            print()
            print(f"Microphone error: {e}")
            print("Restarting microphone...")
            continue

        except Exception as e:

            print()
            print(f"Unexpected error: {e}")
            continue

        # ----------------------------------------------
        # MEMORY
        # ----------------------------------------------

        handle_memory(user_input)

        # ----------------------------------------------
        # INPUT LANGUAGE
        # ----------------------------------------------

        language = detect_language(
            user_input
        )

        print(
            f"Language: {language}"
        )

        # ----------------------------------------------
        # EXIT
        # ----------------------------------------------

        if is_exit_command(user_input):

            if language == "hi":

                await speak(
                    "अलविदा। अपना ख्याल रखना।",
                    language="hi"
                )

            else:

                await speak(
                    "Goodbye. Take care.",
                    language="en"
                )

            break

        # ----------------------------------------------
        # ARIA BRAIN
        # ----------------------------------------------

        reply = get_reply(
            user_input=user_input,
            language=language
        )

        print(
            f"Aria: {reply}"
        )

        # ----------------------------------------------
        # DETECT LANGUAGE OF ACTUAL ARIA RESPONSE
        # ----------------------------------------------

        if re.search(
            r"[\u0900-\u097F]",
            reply
        ):
            output_language = "hi"
        else:
            output_language = "en"

        print(
            f"Aria output language: {output_language}"
        )

        # ----------------------------------------------
        # SPEAK
        # ----------------------------------------------

        await speak(
            reply,
            language=output_language
        )


# ==========================================================
# START ARIA
# ==========================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print()
        print("Aria stopped.")