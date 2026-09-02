import asyncio
from core.speech_to_text import listen
from core.text_to_speech import speak

async def main():
    print("Aria is ready...")

    while True:
        # Listen to user
        user_input = listen()

        if not user_input:
            continue

        # Exit condition
        if "exit" in user_input or "stop" in user_input or "goodbye" in user_input:
            await speak("Goodbye. Take care.")
            break

        # For now, simple reply (we will connect AI brain later)
        if "hello" in user_input or "hi" in user_input:
            reply = "Hello! I'm Aria. How can I help you?"
        elif "your name" in user_input:
            reply = "My name is Aria. I'm your personal assistant."
        elif "how are you" in user_input:
            reply = "I'm doing well. Thank you for asking."
        else:
            reply = "I heard you. I am still learning, but I'm here with you."

        # Speak the reply
        await speak(reply)


if __name__ == "__main__":
    asyncio.run(main())