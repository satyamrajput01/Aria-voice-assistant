import asyncio

import re

from core.speech_to_text import listen

from core.text_to_speech import speak

from core.brain import get_reply

from core.memory import save_memory

from commands.intent import detect_intent


# ==========================================================
# LANGUAGE DETECTION
# ==========================================================
def detect_language(text: str):

    """
    Detect English, Hindi, and Hinglish.
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
        "good", "great", "bad", "fine", "okay",
        "better", "best", "worst",
        "feel", "feeling", "felt",
        "love", "like", "want", "need",
        "talk", "speak", "listen", "help",
        "tell", "give", "show",
        "what", "why", "how", "when",
        "where", "who",
        "hello", "hey", "hi",
        "please", "thanks", "thank",
        "joke", "funny",
        "computer", "phone", "laptop",
        "code", "coding", "project",
        "college", "university",
        "student", "developer",
        "engineering", "course",
    }

    # ------------------------------------------------------
    # ROMANIZED HINDI / HINGLISH
    # ------------------------------------------------------

    hindi_words = {
        "main", "mai", "mein",

        "mujhe", "mujh", "mujhse",

        "mera", "meri", "mere",

        "hum", "ham",

        "humara", "hamara",

        "humari", "hamari",

        "tum", "tumhe", "tumse",

        "tumhara", "tumhari", "tumhare",

        "aap", "aapko",

        "aapka", "aapki", "aapke",

        "hai", "hain", "ho",

        "hun", "hoon",

        "tha", "thi", "the",

        "raha", "rahi", "rahe",

        "kar", "karke",

        "karna", "karne",

        "karo", "karte", "karti",

        "kiya", "kiye",

        "gaya", "gayi", "gaye",

        "aa", "aana", "aaya", "aayi",

        "jaa", "jana", "jane",

        "jao", "jaana",

        "de", "dena", "diya", "do",

        "lelo", "lena", "liya",

        "bata", "batao", "batana",

        "bol", "bolo",

        "sun", "suno",

        "dekh", "dekho",

        "dikha", "dikhao",

        "aaj", "kal", "abhi",

        "bahut", "bohot",

        "achcha", "achha",

        "accha", "acha",

        "bura",

        "kya", "kyu", "kyun",

        "kaise", "kaisa", "kaisi",

        "kab", "kahan", "kahaan",

        "kaun",

        "kyon", "kyunki", "kyonki",

        "nahi", "nahin",

        "haan",

        "yaar", "bhai", "dost",

        "baat", "baatein", "baatain",

        "kuch", "kuchh",

        "sab", "sabhi",

        "sirf",

        "phir", "fir",

        "ab",

        "toh", "to",

        "bhi",

        "hi", "aur",

        "lekin", "magar",

        "isliye",

        "agar",

        "jab",

        "jabki",

        "jo",

        "yeh", "ye",

        "woh", "vo",

        "iska", "iski",

        "uska", "uski",

        "chahiye",

        "chahta", "chahti", "chahte",

        "sakta", "sakti", "sakte",

        "pata",

        "malum", "maalum",

        "samajh",

        "samjha", "samjhi",

        "samajhta", "samajhti",

        "lag", "lagta",

        "lagti", "laga",

        "rakh", "rakhna", "rakho",

        "yaad",

        "bhool", "bhul",

        "time",

        "din", "raat",

        "subah", "shaam",

        "ghar",

        "college",

        "padhai",

        "padhta", "padhti",

        "student",

        "log", "insaan",
    }

    # ------------------------------------------------------
    # ROMANIZED TEXT ANALYSIS
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

    if hindi_matches >= 2:
        return "hi"

    if total_words <= 3 and hindi_matches >= 1:
        return "hi"

    if english_matches >= 1 and hindi_matches == 0:
        return "en"

    # ------------------------------------------------------
    # DEVANAGARI
    # ------------------------------------------------------

    has_devanagari = any(
        "\u0900" <= ch <= "\u097F"
        for ch in text
    )

    if has_devanagari:

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
            "एवरीthing",
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

    return "en"


# ==========================================================
# MEMORY UTILITIES
# ==========================================================

def clean_memory_value(value: str) -> str:

    if not value:
        return ""

    value = value.strip()

    patterns = [
        r",?\s\*please remember( this| it)?\.\*?$",
        r",?\s\*remember( this| it)?\.\*?$",
        r",?\s\*do remember( this| it)?\.\*?$",
        r",?\s\*yaad rakhna\.\*?$",
        r",?\s\*yaad rakhna please\.\*?$",
        r",?\s\*yaad rakhna isey\.\*?$",
    ]

    for pattern in patterns:

        value = re.sub(
            pattern,
            "",
            value,
            flags=re.IGNORECASE
        )

    return value.strip(" .,!?-")


def clean_phrase(value: str) -> str:

    value = clean_memory_value(value)

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def valid_memory_value(value: str) -> bool:

    if not value:
        return False

    value = value.strip()

    if len(value) < 2:
        return False

    if len(value) > 200:
        return False

    return True


# ==========================================================
# SMART PERSONAL MEMORY
# ==========================================================

def handle_memory(user_input: str):

    text = user_input.strip()

    if not text:
        return False

    # ======================================================
    # NAME
    # ======================================================

    name_patterns = [
        r"^my name is (.+)$",
        r"^i'm called (.+)$",
        r"^i am called (.+)$",
        r"^mera naam (.+?) hai$",
        r"^mera naam (.+?) h$",
        r"^main (.+?) hoon$",
        r"^mai (.+?) hoon$",
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
        "really",
        "very",
    }

    for pattern in name_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        name = clean_phrase(
            match.group(1)
        )

        words = name.split()

        if not words:
            continue

        if len(words) > 2:
            continue

        if words[0].lower() in invalid_name_words:
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

    # ======================================================
    # COLLEGE / UNIVERSITY
    # ======================================================

    education_patterns = [
        r"^i study at (.+)$",
        r"^i'm studying at (.+)$",
        r"^i am studying at (.+)$",
        r"^i go to (.+)$",
        r"^i study in (.+)$",
        r"^i am from (.+) university$",
        r"^main (.+?) mein padhta hoon$",
        r"^main (.+?) mein padhti hoon$",
        r"^mai (.+?) mein padhta hoon$",
        r"^mai (.+?) mein padhti hoon$",
    ]

    for pattern in education_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        college = clean_phrase(
            match.group(1)
        )

        if not valid_memory_value(college):
            continue

        save_memory(
            "education",
            "college",
            college
        )

        print(
            f"Memory saved: college = {college}"
        )

        return True

    # ======================================================
    # COURSE / DEGREE
    # ======================================================

    course_patterns = [
        r"^my course is (.+)$",
        r"^my degree is (.+)$",
        r"^i am doing (.+)$",
        r"^i'm doing (.+)$",
        r"^i am studying (.+)$",
        r"^i'm studying (.+)$",
    ]

    for pattern in course_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        course = clean_phrase(
            match.group(1)
        )

        blocked = {
            "this",
            "that",
            "it",
            "coding",
            "a project",
            "something",
            "nothing",
        }

        if course.lower() in blocked:
            continue

        if not valid_memory_value(course):
            continue

        save_memory(
            "education",
            "course",
            course
        )

        print(
            f"Memory saved: course = {course}"
        )

        return True

    # ======================================================
    # PROJECT
    # ======================================================

    project_patterns = [
        r"^i am building (.+)$",
        r"^i'm building (.+)$",
        r"^i am making (.+)$",
        r"^i'm making (.+)$",
        r"^i am creating (.+)$",
        r"^i'm creating (.+)$",
        r"^i am developing (.+)$",
        r"^i'm developing (.+)$",
        r"^i built (.+)$",
    ]

    for pattern in project_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        project = clean_phrase(
            match.group(1)
        )

        if not valid_memory_value(project):
            continue

        save_memory(
            "projects",
            "current_project",
            project
        )

        print(
            f"Memory saved: current_project = {project}"
        )

        return True

    # ======================================================
    # LIKES
    # ======================================================

    like_patterns = [
        r"^i like (.+)$",
        r"^i really like (.+)$",
        r"^i enjoy (.+)$",
        r"^mujhe (.+?) pasand hai$",
        r"^mujhe (.+?) pasand h$",
        r"^mujhe (.+?) bahut pasand hai$",
        r"^mujhe (.+?) bohot pasand hai$",
    ]

    for pattern in like_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        thing = clean_phrase(
            match.group(1)
        )

        if not valid_memory_value(thing):
            continue

        save_memory(
            "preferences",
            "likes",
            thing
        )

        print(
            f"Memory saved: likes = {thing}"
        )

        return True

    # ======================================================
    # LOVE
    # ======================================================

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

        if not match:
            continue

        thing = clean_phrase(
            match.group(1)
        )

        if not valid_memory_value(thing):
            continue

        save_memory(
            "preferences",
            "loves",
            thing
        )

        print(
            f"Memory saved: loves = {thing}"
        )

        return True

    # ======================================================
    # FAVORITES
    # ======================================================

    favorite_patterns = [
        r"^my favorite (.+?) is (.+)$",
        r"^my favourite (.+?) is (.+)$",
    ]

    for pattern in favorite_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        category = clean_phrase(
            match.group(1)
        )

        value = clean_phrase(
            match.group(2)
        )

        if not category:
            continue

        if not valid_memory_value(value):
            continue

        save_memory(
            "preferences",
            f"favorite_{category.lower()}",
            value
        )

        print(
            f"Memory saved: favorite {category} = {value}"
        )

        return True

    # ======================================================
    # HINGLISH FAVORITES
    # ======================================================

    hindi_favorite_patterns = [
        r"^meri favorite (.+?) (.+?) hai$",
        r"^mera favorite (.+?) (.+?) hai$",
        r"^meri favourite (.+?) (.+?) hai$",
        r"^mera favourite (.+?) (.+?) hai$",
    ]

    for pattern in hindi_favorite_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        category = clean_phrase(
            match.group(1)
        )

        value = clean_phrase(
            match.group(2)
        )

        if not category:
            continue

        if not valid_memory_value(value):
            continue

        save_memory(
            "preferences",
            f"favorite_{category.lower()}",
            value
        )

        print(
            f"Memory saved: favorite {category} = {value}"
        )

        return True

    # ======================================================
    # EXPLICIT REMEMBER COMMANDS
    # ======================================================

    remember_patterns = [
        r"^remember that (.+)$",
        r"^remember (.+)$",
        r"^please remember that (.+)$",
        r"^please remember (.+)$",
        r"^yaad rakhna ki (.+)$",
        r"^yaad rakhna (.+)$",
    ]

    for pattern in remember_patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        statement = clean_phrase(
            match.group(1)
        )

        if not valid_memory_value(statement):
            continue

        lowered = statement.lower()

        if "my name is " in lowered:

            value = re.sub(
                r"^my name is\s+",
                "",
                statement,
                flags=re.IGNORECASE
            )

            if valid_memory_value(value):

                save_memory(
                    "personal",
                    "name",
                    value
                )

                print(
                    f"Memory saved: name = {value}"
                )

                return True

        if "i study at " in lowered:

            value = re.sub(
                r"^i study at\s+",
                "",
                statement,
                flags=re.IGNORECASE
            )

            if valid_memory_value(value):

                save_memory(
                    "education",
                    "college",
                    value
                )

                print(
                    f"Memory saved: college = {value}"
                )

                return True

        if "i am building " in lowered:

            value = re.sub(
                r"^i am building\s+",
                "",
                statement,
                flags=re.IGNORECASE
            )

            if valid_memory_value(value):

                save_memory(
                    "projects",
                    "current_project",
                    value
                )

                print(
                    f"Memory saved: current_project = {value}"
                )

                return True

        save_memory(
            "personal",
            "fact",
            statement
        )

        print(
            f"Memory saved: fact = {statement}"
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

    return normalized in exit_commands


# ==========================================================
# COMPUTER COMMAND HANDLER
# ==========================================================

async def handle_computer_command(

    user_input: str,

    language: str

) -> bool:

    """
    Handle safe computer commands.

    Chrome profile commands and normal application commands
    are executed by intent.py.
    """

    intent = detect_intent(
        user_input
    )

    if not intent.get("handled"):

        return False

    # ======================================================
    # COMPUTER COMMAND RESPONSE
    # ======================================================

    response = intent.get(
        "response"
    )

    if response:

        print(
            f"Aria: {response}"
        )

        await speak(
            response,
            language=language
        )

    return True


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

            # ------------------------------------------------
            # LISTEN
            # ------------------------------------------------

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

        # ----------------------------------------------------
        # INPUT LANGUAGE
        # ----------------------------------------------------

        language = detect_language(
            user_input
        )

        print(
            f"Language: {language}"
        )

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # COMPUTER COMMAND
        # ----------------------------------------------------

        computer_command_handled = (

            await handle_computer_command(

                user_input=user_input,

                language=language

            )

        )

        if computer_command_handled:

            continue

        # ----------------------------------------------------
        # MEMORY
        # ----------------------------------------------------

        memory_saved = handle_memory(
            user_input
        )

        if memory_saved:

            print(
                "Memory check: useful information detected."
            )

        # ----------------------------------------------------
        # ARIA BRAIN
        # ----------------------------------------------------

        reply = get_reply(

            user_input=user_input,

            language=language

        )

        print(
            f"Aria: {reply}"
        )

        # ----------------------------------------------------
        # RESPONSE LANGUAGE
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # SPEAK
        # ----------------------------------------------------

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