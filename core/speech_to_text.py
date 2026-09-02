import speech_recognition as sr

def listen() -> str:
    """
    Listens from microphone and converts speech to text.
    Returns the recognized text in lowercase.
    """

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Aria is listening...")

        # Adjust for background noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text.lower()

    except sr.UnknownValueError:
        print("Sorry, I could not understand.")
        return ""

    except sr.RequestError:
        print("Speech service is unavailable.")
        return ""


# Test
if __name__ == "__main__":
    result = listen()
    print("Final Output:", result)