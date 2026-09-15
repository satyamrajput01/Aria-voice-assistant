import json
import os
import subprocess
import time
from pathlib import Path

import pygetwindow as gw
import win32api
import win32con
import win32gui
import win32process


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROME_USER_DATA = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Google"
    / "Chrome"
    / "User Data"
)

CHROME_LOCAL_STATE = CHROME_USER_DATA / "Local State"

TRACKING_FILE = (
    BASE_DIR
    / "data"
    / "aria_chrome_windows.json"
)


# ============================================================
# PROFILE DISCOVERY
# ============================================================

def get_chrome_profiles():
    """Return all Chrome profiles installed on this computer."""

    if not CHROME_LOCAL_STATE.exists():
        print("Chrome Local State file not found.")
        return []

    try:
        with open(
            CHROME_LOCAL_STATE,
            "r",
            encoding="utf-8"
        ) as file:
            state = json.load(file)

    except Exception as error:
        print(
            f"Could not read Chrome Local State: {error}"
        )
        return []

    profile_cache = (
        state
        .get("profile", {})
        .get("info_cache", {})
    )

    profiles = []

    for directory, info in profile_cache.items():

        if not isinstance(info, dict):
            continue

        profiles.append(
            {
                "name": info.get(
                    "name",
                    directory
                ),
                "directory": directory,
                "email": info.get(
                    "user_name",
                    ""
                ),
            }
        )

    return profiles


def find_profile_by_alias(target):
    """
    Find a Chrome profile by name or directory.

    target may be:
        "ragha"

    or a profile dictionary.
    """

    if isinstance(target, dict):
        return target

    if not target:
        return None

    target = str(target).strip().lower()

    profiles = get_chrome_profiles()

    # Exact name
    for profile in profiles:

        if profile["name"].lower() == target:
            return profile

    # Exact directory
    for profile in profiles:

        if profile["directory"].lower() == target:
            return profile

    # Partial name
    matches = [
        profile
        for profile in profiles
        if target in profile["name"].lower()
    ]

    if len(matches) == 1:
        return matches[0]

    return None


# ============================================================
# CHROME WINDOW DISCOVERY
# ============================================================

def get_chrome_windows():
    """Return visible Chrome windows."""

    windows = []

    try:
        all_windows = gw.getAllWindows()

    except Exception as error:

        print(
            f"Could not read Windows windows: {error}"
        )

        return windows

    for window in all_windows:

        try:

            title = window.title

            if not title:
                continue

            if "Chrome" not in title:
                continue

            handle = int(window._hWnd)

            try:

                _, pid = (
                    win32process
                    .GetWindowThreadProcessId(
                        handle
                    )
                )

            except Exception:

                pid = None

            windows.append(
                {
                    "handle": handle,
                    "pid": pid,
                    "title": title,
                    "width": window.width,
                    "height": window.height,
                }
            )

        except Exception:

            continue

    return windows


def get_chrome_window_handles():

    return {
        window["handle"]
        for window in get_chrome_windows()
    }


# ============================================================
# TRACKING
# ============================================================

def _ensure_tracking_directory():

    TRACKING_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


def _load_tracking():

    _ensure_tracking_directory()

    if not TRACKING_FILE.exists():
        return {}

    try:

        with open(
            TRACKING_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):
            return data

    except Exception as error:

        print(
            f"Could not read tracking data: {error}"
        )

    return {}


def _save_tracking(data):

    _ensure_tracking_directory()

    try:

        with open(
            TRACKING_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

        return True

    except Exception as error:

        print(
            f"Could not save tracking data: {error}"
        )

        return False


def _remove_tracking(profile_directory):

    tracking = _load_tracking()

    if profile_directory in tracking:

        del tracking[profile_directory]

        _save_tracking(tracking)


def _is_window_alive(handle):

    try:

        handle = int(handle)

        return bool(
            win32gui.IsWindow(handle)
        )

    except Exception:

        return False


# ============================================================
# CHROME EXECUTABLE
# ============================================================

def _find_chrome_executable():

    possible_paths = [

        Path(
            os.environ.get(
                "PROGRAMFILES",
                ""
            )
        )
        / "Google"
        / "Chrome"
        / "Application"
        / "chrome.exe",

        Path(
            os.environ.get(
                "PROGRAMFILES(X86)",
                ""
            )
        )
        / "Google"
        / "Chrome"
        / "Application"
        / "chrome.exe",

        Path(
            os.environ.get(
                "LOCALAPPDATA",
                ""
            )
        )
        / "Google"
        / "Chrome"
        / "Application"
        / "chrome.exe",
    ]

    for path in possible_paths:

        if path.exists():
            return str(path)

    return None


# ============================================================
# OPEN CHROME PROFILE
# ============================================================

def open_chrome_profile(target):
    """
    Open a specific Chrome profile.
    """

    if isinstance(target, dict):

        profile = target

    else:

        profile = find_profile_by_alias(target)

    if not profile:

        print(
            f"Chrome profile not found: {target}"
        )

        return None

    chrome_exe = _find_chrome_executable()

    if not chrome_exe:

        print(
            "Chrome executable not found."
        )

        return None

    print(
        f"Opening Chrome profile: "
        f"{profile['name']}"
    )

    print(
        f"Profile directory: "
        f"{profile['directory']}"
    )

    # --------------------------------------------------------
    # Check if Aria already tracks this profile
    # --------------------------------------------------------

    tracking = _load_tracking()

    existing = tracking.get(
        profile["directory"]
    )

    if existing:

        handle = existing.get(
            "window_handle"
        )

        if handle and _is_window_alive(handle):

            print(
                f"Chrome profile "
                f"{profile['name']} "
                "is already open."
            )

            for window in get_chrome_windows():

                if window["handle"] == int(handle):

                    return {
                        "profile": profile,
                        "window": window,
                    }

    # --------------------------------------------------------
    # Existing Chrome windows
    # --------------------------------------------------------

    existing_handles = (
        get_chrome_window_handles()
    )

    # --------------------------------------------------------
    # Start Chrome
    # --------------------------------------------------------

    command = [
        chrome_exe,
        f"--user-data-dir={CHROME_USER_DATA}",
        f"--profile-directory={profile['directory']}",
        "--new-window",
    ]

    print("Starting Chrome...")

    try:

        subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    except Exception as error:

        print(
            f"Could not start Chrome: {error}"
        )

        return None

    # --------------------------------------------------------
    # Wait for Chrome window
    # --------------------------------------------------------

    new_window = None

    for _ in range(100):

        time.sleep(0.15)

        current_windows = (
            get_chrome_windows()
        )

        for window in current_windows:

            if (
                window["handle"]
                not in existing_handles
            ):

                new_window = window
                break

        if new_window:
            break

    if not new_window:

        print(
            "Chrome started but Aria could not "
            "detect the new window."
        )

        return None

    print(
        f"Chrome window opened."
    )

    print(
        f"Window title: "
        f"{new_window['title']}"
    )

    print(
        f"Window handle: "
        f"{new_window['handle']}"
    )

    print(
        f"Window PID: "
        f"{new_window['pid']}"
    )

    return {
        "profile": profile,
        "window": new_window,
    }


# ============================================================
# CLOSE WINDOW USING WINDOWS API
# ============================================================

def _close_window_with_win32(handle):
    """
    Ask the exact Windows window to close.

    This sends WM_CLOSE only to the supplied handle.
    It does NOT kill Chrome's process.
    """

    try:

        handle = int(handle)

    except (TypeError, ValueError):

        return False

    if not _is_window_alive(handle):

        return True

    try:

        win32api.PostMessage(
            handle,
            win32con.WM_CLOSE,
            0,
            0
        )

        return True

    except Exception as error:

        print(
            f"WM_CLOSE failed: {error}"
        )

        return False


def _force_destroy_window(handle):
    """
    Last-resort Windows API attempt.

    Only operates on the exact window handle.
    """

    try:

        handle = int(handle)

    except (TypeError, ValueError):

        return False

    if not _is_window_alive(handle):

        return True

    try:

        win32gui.PostMessage(
            handle,
            win32con.WM_SYSCOMMAND,
            win32con.SC_CLOSE,
            0
        )

        return True

    except Exception as error:

        print(
            f"SC_CLOSE failed: {error}"
        )

        return False


# ============================================================
# CLOSE SPECIFIC CHROME WINDOW
# ============================================================

def close_chrome_window(handle):

    try:

        handle = int(handle)

    except (TypeError, ValueError):

        print(
            f"Invalid Chrome window handle: {handle}"
        )

        return False

    print(
        f"Closing Chrome window: {handle}"
    )

    if not _is_window_alive(handle):

        print(
            f"Chrome window {handle} "
            "is already closed."
        )

        return True

    # --------------------------------------------------------
    # Method 1: pygetwindow
    # --------------------------------------------------------

    try:

        window = gw.Win32Window(handle)

        window.close()

    except Exception as error:

        print(
            f"Normal window close failed: {error}"
        )

    # --------------------------------------------------------
    # Wait for normal close
    # --------------------------------------------------------

    for _ in range(30):

        time.sleep(0.1)

        if not _is_window_alive(handle):

            print(
                f"Chrome window {handle} "
                "closed successfully."
            )

            return True

    # --------------------------------------------------------
    # Method 2: Windows WM_CLOSE
    # --------------------------------------------------------

    print(
        "Normal close did not work."
    )

    print(
        "Trying Windows WM_CLOSE..."
    )

    _close_window_with_win32(handle)

    for _ in range(30):

        time.sleep(0.1)

        if not _is_window_alive(handle):

            print(
                f"Chrome window {handle} "
                "closed successfully."
            )

            return True

    # --------------------------------------------------------
    # Method 3: Windows SC_CLOSE
    # --------------------------------------------------------

    print(
        "WM_CLOSE did not close the window."
    )

    print(
        "Trying Windows SC_CLOSE..."
    )

    _force_destroy_window(handle)

    for _ in range(30):

        time.sleep(0.1)

        if not _is_window_alive(handle):

            print(
                f"Chrome window {handle} "
                "closed successfully."
            )

            return True

    # --------------------------------------------------------
    # Final verification
    # --------------------------------------------------------

    print(
        f"Chrome window {handle} "
        "could not be closed."
    )

    return False


# ============================================================
# MANAGED CHROME OPEN
# ============================================================

def open_managed_chrome_profile(target):

    result = open_chrome_profile(
        target
    )

    if not result:
        return False

    profile = result["profile"]
    window = result["window"]

    tracking = _load_tracking()

    tracking[
        profile["directory"]
    ] = {
        "profile_name": profile["name"],
        "profile_directory": profile["directory"],
        "window_handle": window["handle"],
        "window_pid": window["pid"],
        "window_title": window["title"],
    }

    if not _save_tracking(tracking):

        print(
            "Chrome opened but tracking "
            "information could not be saved."
        )

        return False

    print(
        f"Aria is now tracking Chrome "
        f"profile {profile['name']}."
    )

    return True


# ============================================================
# MANAGED CHROME CLOSE
# ============================================================

def close_managed_chrome_profile(target):
    """
    Close only the Chrome window tracked by Aria
    for the requested profile.
    """

    if isinstance(target, dict):

        profile = target

    else:

        profile = find_profile_by_alias(target)

    if not profile:

        print(
            f"Chrome profile not found: {target}"
        )

        return False

    tracking = _load_tracking()

    profile_directory = (
        profile["directory"]
    )

    tracked = tracking.get(
        profile_directory
    )

    if not tracked:

        print(
            f"No tracked Chrome window "
            f"found for {profile['name']}."
        )

        return False

    handle = tracked.get(
        "window_handle"
    )

    if not handle:

        print(
            f"No window handle stored for "
            f"{profile['name']}."
        )

        _remove_tracking(
            profile_directory
        )

        return False

    print(
        f"Aria found tracked Chrome window "
        f"for {profile['name']}."
    )

    print(
        f"Tracked window handle: {handle}"
    )

    success = close_chrome_window(
        handle
    )

    if success:

        _remove_tracking(
            profile_directory
        )

        print(
            f"Aria stopped tracking Chrome "
            f"profile {profile['name']}."
        )

        return True

    print(
        f"Could not close Chrome profile "
        f"{profile['name']}."
    )

    return False


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def close_chrome_profile(target):

    return close_managed_chrome_profile(
        target
    )


# ============================================================
# MANAGED PROFILES
# ============================================================

def get_managed_chrome_profiles():

    tracking = _load_tracking()

    active = {}

    for directory, info in tracking.items():

        handle = info.get(
            "window_handle"
        )

        if (
            handle
            and _is_window_alive(handle)
        ):

            active[directory] = info

    if active != tracking:

        _save_tracking(active)

    return active


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print(
        "\n=== Chrome Profiles ==="
    )

    profiles = get_chrome_profiles()

    if not profiles:

        print(
            "No Chrome profiles found."
        )

    else:

        for profile in profiles:

            print(
                f"{profile['name']} "
                f"-> {profile['directory']}"
            )

    print(
        "\n=== Chrome Windows ==="
    )

    windows = get_chrome_windows()

    if not windows:

        print(
            "No Chrome windows found."
        )

    else:

        for window in windows:

            print(
                f"TITLE: {window['title']} "
                f"| HANDLE: {window['handle']} "
                f"| PID: {window['pid']}"
            )

    print(
        "\n=== Aria Managed Chrome ==="
    )

    managed = (
        get_managed_chrome_profiles()
    )

    if not managed:

        print(
            "No Chrome windows are "
            "currently managed."
        )

    else:

        for directory, info in managed.items():

            print(
                f"{directory} "
                f"-> HANDLE "
                f"{info['window_handle']} "
                f"-> {info['window_title']}"
            )