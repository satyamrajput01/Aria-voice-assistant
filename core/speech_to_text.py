import speech_recognition as sr

def listen() -> str:
    """
    Listens from microphone and converts speech to text.
    Supports both Hindi and English.
    """

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Aria is listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        # First try English
        try:
            text = recognizer.recognize_google(audio, language="en-IN")
            print(f"You said: {text}")
            return text.lower()
        except:
            # If English fails, try Hindi
            text = recognizer.recognize_google(audio, language="hi-IN")
            print(f"You said: {text}")
            return text.lower()

    except sr.UnknownValueError:
        print("Sorry, I could not understand.")
        return ""

    except sr.RequestError:
        print("Speech service is unavailable.")
        return ""


if __name__ == "__main__":
    result = listen()
    print("Final Output:", result)