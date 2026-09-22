import os
import re
import subprocess
import time
from difflib import SequenceMatcher
from pathlib import Path

import pygetwindow as gw


# ============================================================
# BASIC PATHS
# ============================================================

HOME = Path.home()

FOLDER_SEARCH_PATHS = [
    HOME / "Desktop",
    HOME / "Downloads",
    HOME / "Documents",
]


# ============================================================
# VS CODE TRACKING
# ============================================================

_tracked_vscode_hwnd = None


def get_vscode_windows():
    """
    Return currently visible VS Code windows.
    """
    windows = []

    try:
        for window in gw.getAllWindows():
            title = (window.title or "").strip().lower()

            if (
                "visual studio code" in title
                or title.endswith(" - code")
                or title.endswith(" - visual studio code")
            ):
                windows.append(window)

    except Exception as error:
        print("VS Code window detection error:", error)

    return windows


def open_tracked_vscode(path):
    """
    Open VS Code in a new window and remember the exact window handle.
    """
    global _tracked_vscode_hwnd

    path = os.path.abspath(path)

    if not os.path.exists(path):
        return {
            "success": False,
            "response": f"VS Code path does not exist: {path}",
        }

    existing_hwnds = {
        window._hWnd
        for window in get_vscode_windows()
        if getattr(window, "_hWnd", None)
    }

    try:
        subprocess.Popen(
            [path, "--new-window"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    except Exception as error:
        return {
            "success": False,
            "response": f"Could not open VS Code: {error}",
        }

    deadline = time.time() + 15

    while time.time() < deadline:
        time.sleep(0.5)

        try:
            windows = get_vscode_windows()

            for window in windows:
                hwnd = getattr(window, "_hWnd", None)

                if hwnd and hwnd not in existing_hwnds:
                    _tracked_vscode_hwnd = hwnd

                    return {
                        "success": True,
                        "name": "Visual Studio Code",
                        "path": path,
                        "hwnd": hwnd,
                        "response": "Opened Visual Studio Code.",
                    }

        except Exception:
            pass

    return {
        "success": True,
        "name": "Visual Studio Code",
        "path": path,
        "response": "Opened Visual Studio Code.",
    }


def close_tracked_vscode():
    """
    Close only the VS Code window opened/tracked by Aria.
    """
    global _tracked_vscode_hwnd

    if not _tracked_vscode_hwnd:
        return {
            "success": False,
            "response": "There is no tracked VS Code window to close.",
        }

    target_hwnd = _tracked_vscode_hwnd

    try:
        windows = get_vscode_windows()

        target_window = None

        for window in windows:
            if getattr(window, "_hWnd", None) == target_hwnd:
                target_window = window
                break

        if target_window is None:
            _tracked_vscode_hwnd = None

            return {
                "success": True,
                "response": "The tracked VS Code window is already closed.",
            }

        try:
            target_window.close()
        except Exception as error:
            print("VS Code close request error:", error)

        time.sleep(1)

        remaining_hwnds = {
            getattr(window, "_hWnd", None)
            for window in get_vscode_windows()
        }

        if target_hwnd not in remaining_hwnds:
            _tracked_vscode_hwnd = None

            return {
                "success": True,
                "response": "Closed the tracked VS Code window.",
            }

        return {
            "success": False,
            "response": "VS Code window is still open.",
        }

    except Exception as error:
        return {
            "success": False,
            "response": f"Could not close tracked VS Code: {error}",
        }


# ============================================================
# APPLICATION ALIASES
# ============================================================

ALIASES = {
    # VS Code
    "vs code": "visual studio code",
    "vscode": "visual studio code",
    "visual studio code": "visual studio code",
    "code": "visual studio code",

    # Chrome
    "chrome": "google chrome",
    "google chrome": "google chrome",

    # Edge
    "edge": "microsoft edge",
    "microsoft edge": "microsoft edge",

    # Comet
    "comet": "comet",
    "comet browser": "comet",
    "comet browser app": "comet",

    # Notepad
    "notepad": "notepad",
    "note pad": "notepad",

    # Calculator
    "calculator": "calculator",
    "calc": "calculator",

    # File Explorer
    "explorer": "file explorer",
    "file explorer": "file explorer",
    "files": "file explorer",
    "file manager": "file explorer",

    # Terminal
    "terminal": "windows terminal",
    "windows terminal": "windows terminal",

    # CMD
    "cmd": "command prompt",
    "command prompt": "command prompt",
    "command line": "command prompt",

    # PowerShell
    "powershell": "powershell",
    "power shell": "powershell",
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize speech/user input for application and folder matching.
    """
    if not text:
        return ""

    text = str(text).lower().strip()

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    # Remove common file extensions.
    text = re.sub(r"\.(exe|lnk|url)$", "", text)

    # Normalize spaces.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# SIMILARITY
# ============================================================

def similarity(a, b):
    """
    Return similarity ratio between two strings.
    """
    a = normalize_text(a)
    b = normalize_text(b)

    if not a or not b:
        return 0.0

    if a == b:
        return 1.0

    if a in b or b in a:
        return 0.95

    return SequenceMatcher(None, a, b).ratio()


def get_aliases(query):
    """
    Return possible aliases for a query.
    """
    normalized = normalize_text(query)

    aliases = [normalized]

    if normalized in ALIASES:
        aliases.append(ALIASES[normalized])

    for alias, target in ALIASES.items():
        if target == normalized:
            aliases.append(alias)

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(aliases))


# ============================================================
# START MENU APPLICATION SEARCH
# ============================================================

def get_start_menu_apps():
    """
    Get Windows Start Menu applications using PowerShell.

    Returns:
        [
            {
                "name": "...",
                "app_id": "..."
            }
        ]
    """

    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-StartApps | ForEach-Object { "
        "Write-Output ($_.Name + '||' + $_.AppID) "
        "}",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )

        apps = []

        for line in result.stdout.splitlines():
            line = line.strip()

            if "||" not in line:
                continue

            name, app_id = line.split("||", 1)

            if name.strip():
                apps.append(
                    {
                        "name": name.strip(),
                        "app_id": app_id.strip(),
                    }
                )

        return apps

    except Exception as error:
        print("Start Menu search error:", error)
        return []


# ============================================================
# PATH EXECUTABLE SEARCH
# ============================================================

def find_executable_on_path(query):
    """
    Find an executable available through PATH.
    """

    aliases = get_aliases(query)

    for alias in aliases:
        try:
            result = subprocess.run(
                ["where", f"{alias}.exe"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )

            if result.returncode == 0:
                lines = [
                    line.strip()
                    for line in result.stdout.splitlines()
                    if line.strip()
                ]

                if lines:
                    return lines[0]

        except Exception:
            pass

    return None


# ============================================================
# VS CODE DISCOVERY
# ============================================================

def find_vscode():
    """
    Find VS Code executable from common Windows locations,
    then fall back to PATH.
    """

    possible_paths = [
        HOME
        / "AppData"
        / "Local"
        / "Programs"
        / "Microsoft VS Code"
        / "Code.exe",

        Path(os.environ.get("ProgramFiles", ""))
        / "Microsoft VS Code"
        / "Code.exe",

        Path(os.environ.get("ProgramFiles(x86)", ""))
        / "Microsoft VS Code"
        / "Code.exe",
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    return find_executable_on_path("code")


# ============================================================
# COMMON APPLICATION PATH SEARCH
# ============================================================

def find_common_application_paths(query):
    """
    Search common Windows application directories.
    """

    normalized_query = normalize_text(query)

    roots = []

    local_app_data = os.environ.get("LOCALAPPDATA")
    program_files = os.environ.get("ProgramFiles")
    program_files_x86 = os.environ.get("ProgramFiles(x86)")

    if local_app_data:
        roots.append(Path(local_app_data))

    if program_files:
        roots.append(Path(program_files))

    if program_files_x86:
        roots.append(Path(program_files_x86))

    results = []

    for root in roots:
        if not root.exists():
            continue

        try:
            for path in root.glob("**/*.exe"):
                filename = normalize_text(path.stem)

                score = similarity(
                    normalized_query,
                    filename,
                )

                if (
                    normalized_query in filename
                    or filename in normalized_query
                    or score >= 0.70
                ):
                    results.append(
                        {
                            "name": path.stem,
                            "path": str(path),
                            "score": score,
                            "source": "common_path",
                        }
                    )

        except Exception as error:
            print(
                f"Application search error in {root}:",
                error,
            )

    return results


# ============================================================
# APPLICATION SEARCH
# ============================================================

def search_applications(query):
    """
    Search installed applications dynamically.

    Sources:
    - aliases
    - VS Code
    - Windows Start Menu
    - PATH
    - common application folders
    """

    normalized_query = normalize_text(query)

    if not normalized_query:
        return []

    results = []

    # --------------------------------------------------------
    # VS CODE SPECIAL CASE
    # --------------------------------------------------------

    vscode_aliases = {
        "vs code",
        "vscode",
        "visual studio code",
        "code",
    }

    if normalized_query in vscode_aliases:
        vscode_path = find_vscode()

        if vscode_path:
            results.append(
                {
                    "name": "Visual Studio Code",
                    "path": vscode_path,
                    "score": 1.0,
                    "source": "vscode",
                }
            )

    # --------------------------------------------------------
    # ALIASES
    # --------------------------------------------------------

    aliases = get_aliases(normalized_query)

    # --------------------------------------------------------
    # START MENU
    # --------------------------------------------------------

    start_apps = get_start_menu_apps()

    for app in start_apps:
        app_name = normalize_text(app["name"])

        best_score = max(
            similarity(normalized_query, app_name),
            *[
                similarity(alias, app_name)
                for alias in aliases
            ],
        )

        # Special handling for Comet.
        if "comet" in normalized_query and "comet" in app_name:
            best_score = 1.0

        if best_score >= 0.60:
            results.append(
                {
                    "name": app["name"],
                    "app_id": app["app_id"],
                    "score": best_score,
                    "source": "start_menu",
                }
            )

    # --------------------------------------------------------
    # PATH
    # --------------------------------------------------------

    executable = find_executable_on_path(normalized_query)

    if executable:
        results.append(
            {
                "name": Path(executable).stem,
                "path": executable,
                "score": 0.95,
                "source": "path",
            }
        )

    # --------------------------------------------------------
    # COMMON APPLICATION DIRECTORIES
    # --------------------------------------------------------

    results.extend(
        find_common_application_paths(normalized_query)
    )

    # --------------------------------------------------------
    # DEDUPLICATE
    # --------------------------------------------------------

    unique = {}

    for result in results:
        identifier = (
            result.get("path")
            or result.get("app_id")
            or result.get("name")
        )

        identifier = str(identifier).lower()

        if identifier not in unique:
            unique[identifier] = result
        else:
            if result.get("score", 0) > unique[identifier].get(
                "score",
                0,
            ):
                unique[identifier] = result

    results = list(unique.values())

    # Highest score first.
    results.sort(
        key=lambda item: item.get("score", 0),
        reverse=True,
    )

    return results


# ============================================================
# OPEN APPLICATION
# ============================================================

def open_application(query):
    """
    Open an application from a natural-language query.
    """

    normalized_query = normalize_text(query)

    if not normalized_query:
        return {
            "success": False,
            "response": "No application name was provided.",
        }

    # --------------------------------------------------------
    # VS CODE
    # --------------------------------------------------------

    if normalized_query in {
        "vs code",
        "vscode",
        "visual studio code",
        "code",
    }:
        vscode_path = find_vscode()

        if not vscode_path:
            return {
                "success": False,
                "response": "I could not find Visual Studio Code.",
            }

        return open_tracked_vscode(vscode_path)

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    results = search_applications(normalized_query)

    if not results:
        return {
            "success": False,
            "response": f"I could not find {query}.",
        }

    best = results[0]

    # --------------------------------------------------------
    # START MENU APP
    # --------------------------------------------------------

    if best.get("source") == "start_menu":
        app_id = best.get("app_id")

        try:
            subprocess.Popen(
                [
                    "explorer.exe",
                    f"shell:AppsFolder\\{app_id}",
                ]
            )

            return {
                "success": True,
                "name": best.get("name"),
                "response": f"Opened {best.get('name')}.",
            }

        except Exception as error:
            return {
                "success": False,
                "response": f"Could not open {query}: {error}",
            }

    # --------------------------------------------------------
    # NORMAL EXECUTABLE
    # --------------------------------------------------------

    path = best.get("path")

    if path and os.path.exists(path):
        try:
            subprocess.Popen(
                [path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return {
                "success": True,
                "name": best.get("name"),
                "path": path,
                "response": f"Opened {best.get('name')}.",
            }

        except Exception as error:
            return {
                "success": False,
                "response": f"Could not open {query}: {error}",
            }

    return {
        "success": False,
        "response": f"I found {query}, but could not launch it.",
    }


# ============================================================
# PROCESS HELPERS
# ============================================================

PROCESS_MAP = {
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",

    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",

    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",

    # IMPORTANT:
    # Comet uses comet.exe.
    "comet": "comet.exe",
    "comet browser": "comet.exe",

    "terminal": "WindowsTerminal.exe",
    "windows terminal": "WindowsTerminal.exe",

    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",

    "powershell": "powershell.exe",
}


def is_process_running(process_name):
    """
    Check whether a process is currently running.

    Uses tasklist filtering rather than relying on taskkill output.
    """

    try:
        result = subprocess.run(
            [
                "tasklist",
                "/FI",
                f"IMAGENAME eq {process_name}",
                "/NH",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )

        output = result.stdout.lower()

        return process_name.lower() in output

    except Exception as error:
        print(
            f"Process check error for {process_name}:",
            error,
        )
        return False


# ============================================================
# CLOSE APPLICATION
# ============================================================

def close_application(query):
    """
    Safely close supported applications.

    VS Code:
        closes only the exact tracked VS Code window.

    Other supported apps:
        uses taskkill with an explicit process allowlist.

    Comet:
        uses repeated taskkill attempts because the browser
        can have multiple comet.exe processes.
    """

    normalized_query = normalize_text(query)

    if not normalized_query:
        return {
            "success": False,
            "response": "No application name was provided.",
        }

    # --------------------------------------------------------
    # VS CODE SPECIAL CASE
    # --------------------------------------------------------

    if normalized_query in {
        "vs code",
        "vscode",
        "visual studio code",
        "code",
    }:
        return close_tracked_vscode()

    # --------------------------------------------------------
    # FIND PROCESS
    # --------------------------------------------------------

    process_name = PROCESS_MAP.get(normalized_query)

    if not process_name:
        aliases = get_aliases(normalized_query)

        for alias in aliases:
            if alias in PROCESS_MAP:
                process_name = PROCESS_MAP[alias]
                break

    # --------------------------------------------------------
    # COMET SPECIAL HANDLING
    # --------------------------------------------------------

    if normalized_query in {
        "comet",
        "comet browser",
    }:
        process_name = "comet.exe"

    # --------------------------------------------------------
    # UNSUPPORTED APP
    # --------------------------------------------------------

    if not process_name:
        return {
            "success": False,
            "name": normalized_query,
            "response": (
                f"I can open {query}, but I don't have "
                f"permission to close it yet."
            ),
        }

    # --------------------------------------------------------
    # CHECK IF ALREADY CLOSED
    # --------------------------------------------------------

    if not is_process_running(process_name):
        return {
            "success": True,
            "name": normalized_query,
            "process": process_name,
            "response": f"{query} is already closed.",
        }

    # --------------------------------------------------------
    # KILL PROCESS
    # --------------------------------------------------------

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        print(
            f"Closing {process_name} "
            f"(attempt {attempt}/{max_attempts})..."
        )

        try:
            result = subprocess.run(
                [
                    "taskkill",
                    "/IM",
                    process_name,
                    "/F",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )

            if result.stdout:
                print(
                    "taskkill:",
                    result.stdout.strip(),
                )

            if result.stderr:
                print(
                    "taskkill stderr:",
                    result.stderr.strip(),
                )

        except subprocess.TimeoutExpired:
            print(
                f"taskkill timed out for {process_name}."
            )

        except Exception as error:
            print(
                f"taskkill error for {process_name}:",
                error,
            )

        # Give Windows time to terminate child processes.
        time.sleep(1.2)

        # ----------------------------------------------------
        # VERIFY
        # ----------------------------------------------------

        if not is_process_running(process_name):
            return {
                "success": True,
                "name": normalized_query,
                "process": process_name,
                "response": f"Closed {query}.",
            }

    # --------------------------------------------------------
    # STILL RUNNING
    # --------------------------------------------------------

    return {
        "success": False,
        "name": normalized_query,
        "process": process_name,
        "response": (
            f"I tried to close {query}, "
            f"but it is still running."
        ),
    }


# ============================================================
# FOLDER SEARCH
# ============================================================

def search_folders(query):
    """
    Search Desktop, Downloads and Documents recursively.
    """

    normalized_query = normalize_text(query)

    if not normalized_query:
        return []

    results = []

    for root in FOLDER_SEARCH_PATHS:

        if not root.exists():
            continue

        try:
            for path in root.rglob("*"):

                if not path.is_dir():
                    continue

                folder_name = normalize_text(path.name)

                score = similarity(
                    normalized_query,
                    folder_name,
                )

                if (
                    normalized_query in folder_name
                    or folder_name in normalized_query
                    or score >= 0.65
                ):
                    results.append(
                        {
                            "name": path.name,
                            "path": str(path),
                            "score": score,
                            "source": "folder",
                        }
                    )

        except Exception as error:
            print(
                f"Folder search error in {root}:",
                error,
            )

    results.sort(
        key=lambda item: item.get("score", 0),
        reverse=True,
    )

    return results


# ============================================================
# GENERAL COMPUTER SEARCH
# ============================================================

def search_computer(query):
    """
    Search applications and folders.
    """

    applications = search_applications(query)
    folders = search_folders(query)

    return {
        "applications": applications,
        "folders": folders,
    }


# ============================================================
# OPEN SEARCH RESULT
# ============================================================

def open_search_result(result):
    """
    Open an application or folder result returned by search.
    """

    if not result:
        return {
            "success": False,
            "response": "No search result was provided.",
        }

    source = result.get("source")

    # --------------------------------------------------------
    # APPLICATION
    # --------------------------------------------------------

    if source in {
        "start_menu",
        "vscode",
        "path",
        "common_path",
    }:
        if source == "start_menu":
            app_id = result.get("app_id")

            if not app_id:
                return {
                    "success": False,
                    "response": "Application ID is missing.",
                }

            try:
                subprocess.Popen(
                    [
                        "explorer.exe",
                        f"shell:AppsFolder\\{app_id}",
                    ]
                )

                return {
                    "success": True,
                    "response": (
                        f"Opened {result.get('name', 'application')}."
                    ),
                }

            except Exception as error:
                return {
                    "success": False,
                    "response": f"Could not open application: {error}",
                }

        path = result.get("path")

        if not path or not os.path.exists(path):
            return {
                "success": False,
                "response": "Application path does not exist.",
            }

        try:
            subprocess.Popen(
                [path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return {
                "success": True,
                "response": (
                    f"Opened {result.get('name', 'application')}."
                ),
            }

        except Exception as error:
            return {
                "success": False,
                "response": f"Could not open application: {error}",
            }

    # --------------------------------------------------------
    # FOLDER
    # --------------------------------------------------------

    if source == "folder":
        path = result.get("path")

        if not path or not os.path.exists(path):
            return {
                "success": False,
                "response": "Folder path does not exist.",
            }

        try:
            os.startfile(path)

            return {
                "success": True,
                "response": (
                    f"Opened folder {result.get('name', '')}."
                ),
            }

        except Exception as error:
            return {
                "success": False,
                "response": f"Could not open folder: {error}",
            }

    return {
        "success": False,
        "response": "Unknown search result type.",
    }


# ============================================================
# BEST APPLICATION
# ============================================================

def find_best_application(query):
    """
    Return the highest-scoring application.
    """

    results = search_applications(query)

    if not results:
        return None

    return results[0]


# ============================================================
# BEST FOLDER
# ============================================================

def find_best_folder(query):
    """
    Return the highest-scoring folder.
    """

    results = search_folders(query)

    if not results:
        return None

    return results[0]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n=== APPLICATION SEARCH TEST ===")

    for query in [
        "calculator",
        "chrome",
        "comet",
        "vs code",
    ]:
        print(f"\nSearching: {query}")

        results = search_applications(query)

        for result in results[:5]:
            print(result)

    print("\n=== FOLDER SEARCH TEST ===")

    folder_results = search_folders("Aria")

    for result in folder_results[:5]:
        print(result)

    print("\n=== DONE ===")