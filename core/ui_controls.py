
import threading

# Aria starts automatically, preserving your current startup behavior.
_condition = threading.Condition()
_mode = "RUNNING"
_generation = 0

VALID_MODES = {"RUNNING", "PAUSED", "STOPPED"}


def get_control_mode() -> str:
    with _condition:
        return _mode


def get_generation() -> int:
    with _condition:
        return _generation


def is_active(generation: int) -> bool:
    """True only if the same listening session is still active."""
    with _condition:
        return _mode == "RUNNING" and generation == _generation


def wait_until_active() -> None:
    """Wait here while paused or stopped."""
    with _condition:
        while _mode != "RUNNING":
            _condition.wait()


def set_control(command: str) -> str:
    """Apply a UI control command and return the resulting mode."""
    global _mode, _generation

    command = str(command).strip().upper()

    with _condition:
        if command == "START":
            if _mode == "STOPPED":
                _mode = "RUNNING"
                _generation += 1

        elif command == "PAUSE":
            if _mode == "RUNNING":
                _mode = "PAUSED"
                _generation += 1

        elif command == "RESUME":
            if _mode == "PAUSED":
                _mode = "RUNNING"
                _generation += 1

        elif command == "STOP":
            if _mode != "STOPPED":
                _mode = "STOPPED"
                _generation += 1

        else:
            raise ValueError("Unsupported control command")

        _condition.notify_all()
        return _mode
