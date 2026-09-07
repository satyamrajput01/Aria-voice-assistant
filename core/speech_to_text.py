import speech_recognition as sr
import time


recognizer = sr.Recognizer()

# ==================================================
# SPEECH RECOGNITION SETTINGS
# ==================================================

recognizer.pause_threshold = 1.8
recognizer.phrase_threshold = 0.2
recognizer.non_speaking_duration = 0.8

# Automatically adjust to room/background noise
recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 300


def listen():
    """
    Listen to the microphone and convert speech to text.

    Handles microphone and PyAudio errors without crashing Aria.
    """

    try:

        with sr.Microphone() as source:

            print("Aria is listening...")

            try:
                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=15
                )

            except sr.WaitTimeoutError:
                print("No speech detected.")
                return ""

            except OSError as e:
                print(f"Microphone stream error: {e}")
                return ""

    except OSError as e:

        print(f"Microphone error: {e}")
        print("Retrying microphone...")
        time.sleep(1)

        return ""

    except Exception as e:

        print(f"Unexpected microphone error: {e}")
        return ""


    # ==================================================
    # SPEECH TO TEXT
    # ==================================================

    try:

        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        text = text.strip()

        if text:
            print(f"You said: {text}")
            return text

        return ""

    except sr.UnknownValueError:

        print("Sorry, I could not understand.")
        return ""

    except sr.RequestError as e:

        print(f"Speech recognition service error: {e}")
        return ""

    except Exception as e:

        print(f"Speech recognition error: {e}")
        return ""