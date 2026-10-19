import os
import subprocess

from core.ui_state import set_audio_level


# ============================================================
# SETTINGS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

KOKORO_SCRIPT = os.path.join(
    BASE_DIR,
    "kokoro_tts.py",
)


# ============================================================
# LANGUAGE NORMALIZATION
# ============================================================

def normalize_language(language: str) -> str:
    if not language:
        return "en"

    language = str(language).lower().strip()

    if language.startswith("hi"):
        return "hi"

    return "en"


# ============================================================
# LOCAL KOKORO SPEECH
# ============================================================

def speak_with_kokoro(text: str, language: str = "en"):
    text = str(text or "").strip()
    language = normalize_language(language)

    if not text:
        return

    if not os.path.isfile(KOKORO_SCRIPT):
        print(f"Kokoro script not found: {KOKORO_SCRIPT}")
        return

    try:
        print(f"Using local Kokoro TTS ({language})...")

        process = subprocess.run(
            [
                "py",
                "-3.11",
                KOKORO_SCRIPT,
                language,
            ],
            input=text,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=180,
            cwd=BASE_DIR,
        )

        if process.stdout:
            print(process.stdout.strip())

        if process.stderr:
            print("Kokoro:", process.stderr.strip())

        if process.returncode != 0:
            print(
                "Kokoro failed with exit code",
                process.returncode,
            )

    except subprocess.TimeoutExpired:
        print("Kokoro TTS timed out.")

    except Exception as error:
        print("Kokoro TTS error:", repr(error))

    finally:
        set_audio_level(0.0)


# ============================================================
# MAIN TTS FUNCTION
# ============================================================

async def speak(text: str, language: str = "en"):
    if not text or not str(text).strip():
        return

    language = normalize_language(language)

    speak_with_kokoro(
        text=text,
        language=language,
    )
