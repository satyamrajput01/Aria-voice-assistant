import speech_recognition as sr


recognizer = sr.Recognizer()

# Wait longer before deciding you stopped speaking
recognizer.pause_threshold = 2.0
recognizer.phrase_threshold = 0.2
recognizer.non_speaking_duration = 0.8

recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 300


def listen():
    with sr.Microphone() as source:
        print("Listening...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.7
        )

        try:
            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=40
            )

        except sr.WaitTimeoutError:
            print("No speech detected.")
            return "", None

    # --------------------------------------------------------
    # English is primary
    # --------------------------------------------------------

    try:
        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print(f"English recognition: {text}")
        print(f"You said: {text}")

        return text, audio

    except sr.UnknownValueError:
        print("English recognition failed. Trying Hindi...")

    except sr.RequestError as error:
        print(f"Speech recognition service error: {error}")
        return "", audio

    # --------------------------------------------------------
    # Hindi fallback only if English fails
    # --------------------------------------------------------

    try:
        text = recognizer.recognize_google(
            audio,
            language="hi-IN"
        )

        print(f"Hindi recognition: {text}")
        print(f"You said: {text}")

        return text, audio

    except sr.UnknownValueError:
        print("Could not understand audio.")
        return "", audio

    except sr.RequestError as error:
        print(f"Hindi recognition service error: {error}")
        return "", audio