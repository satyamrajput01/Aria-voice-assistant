"""Small, explicit Windows mouse and keyboard controls for Aria.

Only commands parsed by this module are executed. No arbitrary shell commands
or model-generated code are run here.
"""

import ctypes
import os
import re
from ctypes import wintypes

MAX_TYPED_CHARACTERS = 500
MAX_SCROLL_NOTCHES = 10

MODIFIERS = {
    "ctrl": 0x11,
    "control": 0x11,
    "shift": 0x10,
    "alt": 0x12,
}

KEYS = {
    "enter": 0x0D,
    "return": 0x0D,
    "tab": 0x09,
    "space": 0x20,
    "escape": 0x1B,
    "esc": 0x1B,
    "backspace": 0x08,
    "delete": 0x2E,
    "del": 0x2E,
    "home": 0x24,
    "end": 0x23,
    "pageup": 0x21,
    "page up": 0x21,
    "pagedown": 0x22,
    "page down": 0x22,
    "up": 0x26,
    "down": 0x28,
    "left": 0x25,
    "right": 0x27,
    "insert": 0x2D,
    "capslock": 0x14,
    "printscreen": 0x2C,
}

for _letter in "abcdefghijklmnopqrstuvwxyz":
    KEYS[_letter] = ord(_letter.upper())
for _digit in "0123456789":
    KEYS[_digit] = ord(_digit)
for _number in range(1, 13):
    KEYS[f"f{_number}"] = 0x70 + _number - 1

BLOCKED_HOTKEYS = {
    frozenset(("alt", "f4")),
    frozenset(("ctrl", "alt", "delete")),
    frozenset(("ctrl", "shift", "escape")),
    frozenset(("win", "l")),
    frozenset(("ctrl", "w")),
    frozenset(("ctrl", "q")),
    frozenset(("ctrl", "shift", "w")),
}


def _key_name(value):
    value = re.sub(r"\s+", " ", value.strip().lower())
    aliases = {"control": "ctrl", "return": "enter", "esc": "escape", "del": "delete"}
    return aliases.get(value, value)


def _parse_key_sequence(value):
    value = re.sub(r"\bpage\s+up\b", "pageup", value.strip(), flags=re.IGNORECASE)
    value = re.sub(r"\bpage\s+down\b", "pagedown", value, flags=re.IGNORECASE)
    value = re.sub(r"\bcaps\s+lock\b", "capslock", value, flags=re.IGNORECASE)
    parts = [part for part in re.split(r"\s*(?:\+|\s)\s*", value) if part]
    parts = [_key_name(part) for part in parts]
    if not parts or len(parts) > 4 or len(set(parts)) != len(parts):
        return None
    modifiers = [part for part in parts if part in MODIFIERS]
    keys = [part for part in parts if part not in MODIFIERS]
    if len(keys) != 1 or keys[0] not in KEYS:
        return None
    if frozenset(modifiers + keys) in BLOCKED_HOTKEYS:
        return {"error": "That shortcut is blocked because it can close windows or open sensitive system controls."}
    return {"modifiers": modifiers, "key": keys[0]}


def parse_desktop_command(command):
    """Return a validated action dict, or None when this is not a desktop command."""
    if not isinstance(command, str):
        return None
    text = command.strip()
    if not text:
        return None
    lower = text.rstrip(".!?").strip().lower()

    match = re.match(r"^type\s+(.+)$", text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        value = match.group(1).strip()
        if len(value) > MAX_TYPED_CHARACTERS:
            return {"error": f"I can type up to {MAX_TYPED_CHARACTERS} characters at a time."}
        if not value:
            return None
        if value[:1] in ("'", '"') and value[-1:] == value[:1] and len(value) >= 2:
            value = value[1:-1]
        return {"action": "type_text", "text": value}

    match = re.fullmatch(
        r"move\s+(?:the\s+)?(?:mouse|cursor)\s+to\s+(?:x\s*)?(\d+)\s*[, ]\s*(?:y\s*)?(\d+)",
        lower,
    )
    if match:
        return {"action": "move_mouse", "x": int(match.group(1)), "y": int(match.group(2))}

    click_patterns = [
        ("double_click", r"(?:double\s+click|double\s+tap)"),
        ("right_click", r"(?:right\s+click|right\s+tap)"),
        ("left_click", r"(?:left\s+click|left\s+tap|click|tap)"),
    ]
    for action, phrase in click_patterns:
        match = re.fullmatch(phrase + r"(?:\s+at\s+(?:x\s*)?(\d+)\s*[, ]\s*(?:y\s*)?(\d+))?", lower)
        if match:
            result = {"action": action}
            if match.group(1) is not None:
                result.update(x=int(match.group(1)), y=int(match.group(2)))
            return result

    match = re.fullmatch(r"scroll\s+(up|down)(?:\s+(\d+))?(?:\s+(?:notches|steps|times))?", lower)
    if match:
        notches = int(match.group(2) or 3)
        if not 1 <= notches <= MAX_SCROLL_NOTCHES:
            return {"error": f"Scroll amount must be between 1 and {MAX_SCROLL_NOTCHES} notches."}
        return {"action": "scroll", "direction": match.group(1), "notches": notches}

    match = re.fullmatch(r"(?:press|hit)\s+(.+)", lower)
    if not match:
        match = re.fullmatch(r"hotkey\s+(.+)", lower)
    if match:
        sequence = _parse_key_sequence(match.group(1))
        if sequence is None:
            return {"error": "I don't recognise that key or shortcut. Try Enter, Tab, Escape, or Ctrl+S."}
        if "error" in sequence:
            return sequence
        return {"action": "press_key", **sequence}

    return None


# Windows INPUT structures must include the largest union member (MOUSEINPUT).
# Omitting it makes sizeof(INPUT) too small on 64-bit Windows, causing SendInput
# to reject keyboard events with ERROR_INVALID_PARAMETER.
ULONG_PTR = wintypes.WPARAM


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]


def _user32():
    return ctypes.WinDLL("user32", use_last_error=True)


def _send_key(vk, key_up=False):
    user32 = _user32()
    user32.keybd_event.argtypes = [wintypes.BYTE, wintypes.BYTE, wintypes.DWORD, ULONG_PTR]
    user32.keybd_event.restype = None
    flags = 0x0002 if key_up else 0
    user32.keybd_event(vk, 0, flags, 0)


def _type_unicode(value):
    user32 = _user32()
    user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
    user32.SendInput.restype = wintypes.UINT

    inputs = []
    encoded = value.encode("utf-16-le")
    for index in range(0, len(encoded), 2):
        unit = int.from_bytes(encoded[index:index + 2], "little")
        down = INPUT(type=1, ki=KEYBDINPUT(0, unit, 0x0004, 0, 0))
        up = INPUT(type=1, ki=KEYBDINPUT(0, unit, 0x0004 | 0x0002, 0, 0))
        inputs.extend((down, up))

    if not inputs:
        return

    array_type = INPUT * len(inputs)
    array = array_type(*inputs)
    sent = user32.SendInput(len(inputs), array, ctypes.sizeof(INPUT))
    if sent != len(inputs):
        error = ctypes.get_last_error()
        if error:
            raise OSError(error, ctypes.FormatError(error))
        raise OSError(
            "Windows rejected keyboard input. Try running Aria at the same privilege level as the target app."
        )


def execute_desktop_action(action):
    """Execute one parsed action. This first release intentionally supports Windows only."""
    if not isinstance(action, dict):
        return {"success": False, "response": "That desktop action is invalid."}
    if action.get("error"):
        return {"success": False, "response": action["error"]}
    if os.name != "nt":
        return {"success": False, "response": "Mouse and keyboard control is currently supported on Windows only."}

    user32 = _user32()
    kind = action.get("action")

    try:
        if kind in {"move_mouse", "left_click", "right_click", "double_click"}:
            if "x" in action:
                user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
                user32.SetCursorPos.restype = wintypes.BOOL
                width = user32.GetSystemMetrics(0)
                height = user32.GetSystemMetrics(1)
                x, y = action["x"], action["y"]
                if not (0 <= x < width and 0 <= y < height):
                    return {"success": False, "response": f"Coordinates must be within the screen (0–{width - 1}, 0–{height - 1})."}
                if not user32.SetCursorPos(x, y):
                    raise ctypes.WinError(ctypes.get_last_error())
            if kind == "move_mouse":
                return {"success": True, "response": f"Moved the pointer to {action['x']}, {action['y']}."}

            user32.mouse_event.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ULONG_PTR]
            user32.mouse_event.restype = None
            flags = {
                "left_click": (0x0002, 0x0004),
                "right_click": (0x0008, 0x0010),
                "double_click": (0x0002, 0x0004),
            }[kind]
            count = 2 if kind == "double_click" else 1
            for _ in range(count):
                user32.mouse_event(flags[0], 0, 0, 0, 0)
                user32.mouse_event(flags[1], 0, 0, 0, 0)
            label = {"left_click": "Clicked", "right_click": "Right-clicked", "double_click": "Double-clicked"}[kind]
            return {"success": True, "response": f"{label} at the pointer position."}

        if kind == "scroll":
            user32.mouse_event.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ULONG_PTR]
            user32.mouse_event.restype = None
            delta = 120 * action["notches"] * (1 if action["direction"] == "up" else -1)
            user32.mouse_event(0x0800, 0, 0, delta & 0xFFFFFFFF, 0)
            return {"success": True, "response": f"Scrolled {action['direction']} {action['notches']} notches."}

        if kind == "type_text":
            _type_unicode(action["text"])
            return {"success": True, "response": "Typed the requested text."}

        if kind == "press_key":
            modifiers = action["modifiers"]
            key = action["key"]
            for modifier in modifiers:
                _send_key(MODIFIERS[modifier])
            _send_key(KEYS[key])
            _send_key(KEYS[key], key_up=True)
            for modifier in reversed(modifiers):
                _send_key(MODIFIERS[modifier], key_up=True)
            return {"success": True, "response": f"Pressed {'+'.join(modifiers + [key])}."}

        return {"success": False, "response": "That desktop action is not supported."}

    except Exception as error:
        return {"success": False, "response": f"The desktop action failed: {error}"}


def handle_desktop_command(command):
    action = parse_desktop_command(command)
    if action is None:
        return None
    result = execute_desktop_action(action)
    return {
        "handled": True,
        "success": result["success"],
        "action": action.get("action", "desktop_control"),
        "response": result["response"],
    }
