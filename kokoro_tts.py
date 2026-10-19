import sys
import os
import tempfile
import re
import uuid
import time
import json
import urllib.request
import urllib.error

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
# SETTINGS
# ============================================================

SAMPLE_RATE = 24000
CHUNK_SECONDS = 0.04

AUDIO_LEVEL_URL = "http://127.0.0.1:8765/audio-level"


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
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# SEND AUDIO LEVEL TO ARIA UI
# ============================================================

def publish_audio_level(level: float):
    payload = json.dumps({
        "level": float(
            max(0.0, min(1.0, level))
        )
    }).encode("utf-8")

    request = urllib.request.Request(
        AUDIO_LEVEL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=0.25
        ):
            pass

    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
    ):
        # Keep speech working if the UI server is unavailable.
        pass


# ============================================================
# AUDIO LEVEL CALCULATION
# ============================================================

def calculate_audio_levels(audio):
    audio = np.asarray(
        audio,
        dtype=np.float32
    ).reshape(-1)

    if audio.size == 0:
        return [], 1

    chunk_size = max(
        1,
        int(SAMPLE_RATE * CHUNK_SECONDS)
    )

    rms_values = []

    for start in range(0, len(audio), chunk_size):
        chunk = audio[start:start + chunk_size]

        if chunk.size == 0:
            continue

        rms = float(
            np.sqrt(
                np.mean(
                    np.square(chunk)
                )
            )
        )

        rms_values.append(rms)

    if not rms_values:
        return [], chunk_size

    # Use the 95th percentile to normalize the waveform.
    reference = max(
        float(np.percentile(rms_values, 95)),
        0.0001
    )

    levels = [
        min(
            1.0,
            (rms / reference) ** 0.7
        )
        for rms in rms_values
    ]

    return levels, chunk_size


# ============================================================
# REACTIVE PLAYBACK
# ============================================================

def play_audio_with_reactor(filename, audio):
    levels, chunk_size = calculate_audio_levels(audio)

    if not levels:
        print("Kokoro: No audio levels available.")
        return

    print("[KOKORO DEBUG] Starting reactive playback.")

    # Start actual audio playback asynchronously so the
    # level updates can run alongside it.
    winsound.PlaySound(
        filename,
        winsound.SND_FILENAME | winsound.SND_ASYNC
    )

    try:
        for level in levels:
            publish_audio_level(level)

            # Approximate the duration represented by each
            # audio chunk.
            time.sleep(
                chunk_size / SAMPLE_RATE
            )

    finally:
        winsound.PlaySound(None, 0)
        publish_audio_level(0.0)

    print("[KOKORO DEBUG] Playback finished.")


# ============================================================
# KOKORO SPEECH
# ============================================================

def speak(text, language="en"):
    print(f"[KOKORO DEBUG] language = {language}")
    print(f"[KOKORO DEBUG] received text = {repr(text)}")

    text = clean_text(text)

    print(f"[KOKORO DEBUG] cleaned text = {repr(text)}")

    if not text:
        print("Kokoro: No usable text.")
        publish_audio_level(0.0)
        return

    filename = None

    try:
        # ----------------------------------------------------
        # HINDI
        # ----------------------------------------------------

        if language == "hi":
            print(
                "[KOKORO DEBUG] "
                "Using Hindi pipeline: lang_code='h'"
            )

            pipeline = KPipeline(lang_code="h")
            voice = "hf_alpha"

        # ----------------------------------------------------
        # ENGLISH
        # ----------------------------------------------------

        else:
            print(
                "[KOKORO DEBUG] "
                "Using English pipeline: lang_code='a'"
            )

            pipeline = KPipeline(lang_code="a")
            voice = "af_heart"

        print(f"[KOKORO DEBUG] voice = {voice}")

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
            print("Kokoro generated no audio.")
            publish_audio_level(0.0)
            return

        audio = np.concatenate(
            audio_parts
        ).astype(np.float32)

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
            SAMPLE_RATE
        )

        print(f"[KOKORO DEBUG] Playing: {filename}")

        # ----------------------------------------------------
        # PLAY AUDIO + SEND REACTOR LEVELS
        # ----------------------------------------------------

        play_audio_with_reactor(
            filename,
            audio
        )

    except Exception as error:
        print(
            "Kokoro TTS error:",
            repr(error)
        )

    finally:
        publish_audio_level(0.0)

        # Remove the temporary WAV after playback.
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except OSError:
                pass


# ============================================================
# COMMAND LINE ENTRY
# ============================================================

if __name__ == "__main__":
    language = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "en"
    )

    # Read raw bytes and explicitly decode UTF-8.
    raw_input = sys.stdin.buffer.read()

    try:
        text = raw_input.decode("utf-8")
    except UnicodeDecodeError:
        text = raw_input.decode(
            "utf-8",
            errors="replace"
        )

    speak(text, language)