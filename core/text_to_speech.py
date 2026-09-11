import os
import subprocess
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    raise ValueError("ELEVENLABS_API_KEY is missing from .env")

client = ElevenLabs(api_key=api_key)


# ============================================================
# PATHS
# ============================================================

VOICE_ID = "zzyrrX00vfq8JzvcccMi"

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

KOKORO_SCRIPT = os.path.join(
    BASE_DIR,
    "kokoro_tts.py"
)


# ============================================================
# EMOTION SPEED
# ============================================================

def get_speed(emotion: str) -> float:

    if emotion in ["sad", "tired"]:
        return 0.90

    if emotion in ["happy", "excited"]:
        return 1.08

    if emotion == "angry":
        return 0.95

    return 1.0


# ============================================================
# LANGUAGE NORMALIZATION
# ============================================================

def normalize_language(language: str) -> str:

    if not language:
        return "en"

    language = language.lower().strip()

    if language.startswith("hi"):
        return "hi"

    if language.startswith("en"):
        return "en"

    return "en"


# ============================================================
# KOKORO FALLBACK
# ============================================================

def speak_with_kokoro(
    text: str,
    language: str = "en"
):

    if not text:
        return

    language = normalize_language(language)

    print(
        f"Kokoro fallback → language={language}"
    )

    if not os.path.exists(KOKORO_SCRIPT):

        print(
            f"Kokoro script not found: "
            f"{KOKORO_SCRIPT}"
        )

        return

    try:

        process = subprocess.run(
            [
                "py",
                "-3.11",
                KOKORO_SCRIPT,
                language
            ],
            input=text,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=180,
        )

        if process.stdout:

            print(
                process.stdout.strip()
            )

        if process.stderr:

            print(
                "Kokoro:",
                process.stderr.strip()
            )

        if process.returncode != 0:

            print(
                "Kokoro process failed "
                f"with exit code "
                f"{process.returncode}"
            )

        else:

            print(
                "Kokoro finished successfully."
            )

    except subprocess.TimeoutExpired:

        print(
            "Kokoro TTS timed out."
        )

    except Exception as e:

        print(
            "Kokoro TTS error:",
            repr(e)
        )


# ============================================================
# MAIN TTS FUNCTION
# ============================================================

async def speak(
    text: str,
    language: str = "en",
    emotion: str = "neutral"
):

    if not text:
        return

    language = normalize_language(
        language
    )

    # --------------------------------------------------------
    # TRY ELEVENLABS FIRST
    # --------------------------------------------------------

    try:

        print(
            "Using ElevenLabs voice..."
        )

        speed = get_speed(
            emotion
        )

        audio = client.text_to_speech.convert(

            voice_id=VOICE_ID,

            text=text,

            model_id="eleven_multilingual_v2",

            output_format="mp3_44100_128",

            voice_settings={

                "stability": 0.45,

                "similarity_boost": 0.80,

                "style": 0.35,

                "use_speaker_boost": True,

                "speed": speed,
            },
        )

        filename = os.path.join(
            BASE_DIR,
            "aria_output.mp3"
        )

        with open(
            filename,
            "wb"
        ) as f:

            for chunk in audio:

                f.write(chunk)

        print(
            "ElevenLabs voice generated successfully."
        )

        os.startfile(
            filename
        )

        return

    # --------------------------------------------------------
    # ELEVENLABS FAILED → KOKORO
    # --------------------------------------------------------

    except Exception as e:

        print(
            "ElevenLabs TTS error:",
            e
        )

        print(
            "Falling back to local Kokoro..."
        )

        speak_with_kokoro(
            text=text,
            language=language
        )