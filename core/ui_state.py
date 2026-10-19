import threading

_current_state = "IDLE"
_audio_level = 0.0
_lock = threading.Lock()

VALID_STATES = {
    "IDLE",
    "LISTENING",
    "THINKING",
    "EXECUTING",
    "SPEAKING",
    "PAUSED",
    "STOPPED",
}


def set_state(state: str):
    global _current_state

    state = str(state).strip().upper()

    if state not in VALID_STATES:
        return

    with _lock:
        _current_state = state

        if state != "SPEAKING":
            global _audio_level
            _audio_level = 0.0

    print(f"ARIA UI STATE → {state}")


def get_state():
    with _lock:
        return _current_state


def set_audio_level(level: float):
    global _audio_level

    try:
        level = float(level)
    except (TypeError, ValueError):
        level = 0.0

    level = max(0.0, min(1.0, level))

    with _lock:
        _audio_level = level


def get_audio_level():
    with _lock:
        return _audio_level