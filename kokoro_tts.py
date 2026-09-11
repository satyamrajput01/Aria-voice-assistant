import sys
import os
import tempfile
import re
import uuid
 # Force UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    
import numpy as np
import soundfile as sf
import winsound

from kokoro import KPipeline


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:

    if not text:
        return ""

    # Remove invalid Unicode surrogate characters
    text = "".join(
        ch for ch in text
        if not (0xD800 <= ord(ch) <= 0xDFFF)
    )

    # Remove problematic control characters
    text = "".join(
        ch for ch in text
        if ch in "\n\r\t" or ord(ch) >= 32
    )

    # Remove emojis
    text = re.sub(
        r"[\U0001F300-\U0001FAFF]",
        "",
        text
    )

    text = re.sub(
        r"[\u2600-\u27BF]",
        "",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# KOKORO SPEECH
# ============================================================

def speak(text, language="en"):

    print(
        f"[KOKORO DEBUG] language = {language}"
    )

    print(
        f"[KOKORO DEBUG] received text = {repr(text)}"
    )

    text = clean_text(text)

    print(
        f"[KOKORO DEBUG] cleaned text = {repr(text)}"
    )

    if not text:

        print(
            "Kokoro: No usable text."
        )

        return

    try:

        # ----------------------------------------------------
        # HINDI
        # ----------------------------------------------------

        if language == "hi":

            print(
                "[KOKORO DEBUG] "
                "Using Hindi pipeline: lang_code='h'"
            )

            pipeline = KPipeline(
                lang_code="h"
            )

            voice = "hf_alpha"

        # ----------------------------------------------------
        # ENGLISH
        # ----------------------------------------------------

        else:

            print(
                "[KOKORO DEBUG] "
                "Using English pipeline: lang_code='a'"
            )

            pipeline = KPipeline(
                lang_code="a"
            )

            voice = "af_heart"

        print(
            f"[KOKORO DEBUG] voice = {voice}"
        )

        # ----------------------------------------------------
        # GENERATE AUDIO
        # ----------------------------------------------------

        generator = pipeline(
            text,
            voice=voice
        )

        audio_parts = []

        for result in generator:

            if hasattr(result, "output"):

                audio = result.output.audio

            else:

                audio = result[2]

            if audio is not None:

                audio_parts.append(
                    np.asarray(audio)
                )

        if not audio_parts:

            print(
                "Kokoro generated no audio."
            )

            return

        audio = np.concatenate(
            audio_parts
        )

        # ----------------------------------------------------
        # UNIQUE AUDIO FILE
        # ----------------------------------------------------

        filename = os.path.join(
            tempfile.gettempdir(),
            f"aria_kokoro_{uuid.uuid4().hex}.wav"
        )

        sf.write(
            filename,
            audio,
            24000
        )

        print(
            f"[KOKORO DEBUG] Playing: {filename}"
        )

        # ----------------------------------------------------
        # PLAY
        # ----------------------------------------------------

        winsound.PlaySound(
            filename,
            winsound.SND_FILENAME
        )

        print(
            "[KOKORO DEBUG] Playback finished."
        )

    except Exception as e:

        print(
            "Kokoro TTS error:",
            repr(e)
        )


# ============================================================
# COMMAND LINE ENTRY
# ============================================================

if __name__ == "__main__":

    language = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "en"
    )

    # IMPORTANT:
    # Read raw bytes and explicitly decode as UTF-8.
    # This prevents Hindi characters from becoming �.
    raw_input = sys.stdin.buffer.read()

    try:

        text = raw_input.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        text = raw_input.decode(
            "utf-8",
            errors="replace"
        )

    speak(
        text,
        language
    )