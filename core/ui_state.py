import threading


_current_state = "IDLE"
_lock = threading.Lock()


VALID_STATES = {
    "IDLE",
    "LISTENING",
    "THINKING",
    "EXECUTING",
    "SPEAKING",
}


def set_state(state: str):
    global _current_state

    state = str(state).strip().upper()

    if state not in VALID_STATES:
        return

    with _lock:
        _current_state = state

    print(f"ARIA UI STATE → {state}")


def get_state():
    with _lock:
        return _current_state 