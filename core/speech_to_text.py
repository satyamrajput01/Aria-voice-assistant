import speech_recognition as sr
import time


recognizer = sr.Recognizer()


# ==========================================================
# MICROPHONE / SPEECH SETTINGS
# ==========================================================

# Slightly faster conversational response
recognizer.pause_threshold = 0.9

# Lower value helps detect speech sooner
recognizer.phrase_threshold = 0.2

# Amount of silence before considering the phrase finished
recognizer.non_speaking_duration = 0.5

# Automatically adapt to room/microphone noise
recognizer.dynamic_energy_threshold = True

# Starting threshold
recognizer.energy_threshold = 300


# ==========================================================
# LISTEN
# ==========================================================

def listen():
    """
    Listen to the microphone and return:

        (text, audio)

    text:
        Speech converted to text.

    audio:
        Original SpeechRecognition AudioData.
        This is passed to the voice emotion detector.
    """

    try:

        with sr.Microphone() as source:

            print("\n🎤 Aria is listening...")

            # --------------------------------------------------
            # Short ambient-noise calibration
            # --------------------------------------------------
            try:

                recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

            except Exception as e:

                print(
                    f"Microphone calibration warning: {e}"
                )

            # --------------------------------------------------
            # Listen
            # --------------------------------------------------
            try:

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=15
                )

            except sr.WaitTimeoutError:

                print("No speech detected.")
                return None

            except OSError as e:

                print(
                    f"Microphone stream error: {e}"
                )

                return None

    except OSError as e:

        print(
            f"Microphone error: {e}"
        )

        print(
            "Retrying microphone..."
        )

        time.sleep(1)

        return None

    except Exception as e:

        print(
            f"Unexpected microphone error: {e}"
        )

        return None


    # ==========================================================
    # SPEECH RECOGNITION
    # ==========================================================

    # We try Indian English first because most of your
    # English/Hinglish conversation will work well here.

    english_text = None
    hindi_text = None


    # ----------------------------------------------------------
    # English / Indian English
    # ----------------------------------------------------------

    try:

        english_text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        if english_text:

            english_text = english_text.strip()

    except sr.UnknownValueError:

        english_text = None

    except sr.RequestError as e:

        print(
            f"Speech recognition service error: {e}"
        )

        return None

    except Exception as e:

        print(
            f"English recognition error: {e}"
        )


    # ----------------------------------------------------------
    # Hindi
    # ----------------------------------------------------------

    try:

        hindi_text = recognizer.recognize_google(
            audio,
            language="hi-IN"
        )

        if hindi_text:

            hindi_text = hindi_text.strip()

    except sr.UnknownValueError:

        hindi_text = None

    except sr.RequestError as e:

        print(
            f"Hindi speech recognition service error: {e}"
        )

        hindi_text = None

    except Exception as e:

        print(
            f"Hindi recognition error: {e}"
        )


    # ==========================================================
    # CHOOSE BEST RESULT
    # ==========================================================

    if english_text and hindi_text:

        # ------------------------------------------------------
        # If both recognizers understood the audio, decide which
        # result looks more like Hindi/Hinglish.
        # ------------------------------------------------------

        hindi_markers = [
            "main",
            "mai",
            "mujhe",
            "mera",
            "meri",
            "mere",
            "tum",
            "tumse",
            "aap",
            "aapko",
            "kya",
            "kyun",
            "kaise",
            "hai",
            "hoon",
            "haan",
            "nahi",
            "nahin",
            "acha",
            "achha",
            "accha",
            "bahut",
            "thoda",
            "thodi",
            "mujhse",
            "karna",
            "karni",
            "karo",
            "chahiye",
            "lagta",
            "lagti"
        ]


        english_lower = english_text.lower()
        hindi_lower = hindi_text.lower()


        english_words = set(
            english_lower.split()
        )

        hindi_matches = sum(
            1
            for word in hindi_markers
            if word in english_words
        )


        # If English result contains clear Hindi/Hinglish words,
        # prefer it because it preserves the user's natural
        # Hinglish pronunciation better.

        if hindi_matches >= 1:

            text = english_text

        else:

            # Hindi recognizer is more likely to be correct when
            # the English recognizer produces strange text.

            # Compare obvious Devanagari output first.

            if any(
                "\u0900" <= char <= "\u097F"
                for char in hindi_text
            ):

                text = hindi_text

            else:

                text = english_text


        print(
            f"You said: {text}"
        )

        return text, audio


    # ----------------------------------------------------------
    # Only English worked
    # ----------------------------------------------------------

    if english_text:

        print(
            f"You said: {english_text}"
        )

        return english_text, audio


    # ----------------------------------------------------------
    # Only Hindi worked
    # ----------------------------------------------------------

    if hindi_text:

        print(
            f"You said: {hindi_text}"
        )

        return hindi_text, audio


    # ----------------------------------------------------------
    # Neither recognizer understood
    # ----------------------------------------------------------

    print(
        "Sorry, I could not understand."
    )

    return None