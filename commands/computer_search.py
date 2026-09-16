import os
import re
import subprocess
import time
from difflib import SequenceMatcher
from pathlib import Path

import pygetwindow as gw


# ==========================================================
# BASIC PATHS
# ==========================================================

HOME = Path.home()

FOLDER_SEARCH_PATHS = [
    HOME / "Desktop",
    HOME / "Downloads",
    HOME / "Documents",
]


# ==========================================================
# TRACKED VS CODE WINDOW
# ==========================================================

tracked_vscode_window = None


def get_vscode_windows():
    """
    Return currently visible VS Code windows.
    """

    windows = []

    try:
        for window in gw.getAllWindows():

            try:
                title = window.title.strip()
            except Exception:
                continue

            if not title:
                continue

            title_lower = title.lower()

            if (
                "visual studio code" in title_lower
                or title_lower.endswith(" - code")
                or title_lower.endswith(" - visual studio code")
            ):
                windows.append(window)

    except Exception as error:
        print(
            "VS Code window detection error:",
            error
        )

    return windows


def open_tracked_vscode(path):
    """
    Open a NEW VS Code window and remember
    the exact window that was created.
    """

    global tracked_vscode_window

    if not path:
        print(
            "VS Code executable was not found."
        )
        return False

    path = os.path.normpath(path)

    # ------------------------------------------------------
    # IMPORTANT:
    # Only allow the real Code.exe.
    # Never try to execute code.cmd here.
    # ------------------------------------------------------

    if not path.lower().endswith("code.exe"):

        print(
            f"Invalid VS Code executable: {path}"
        )

        return False

    if not os.path.isfile(path):

        print(
            f"VS Code executable does not exist: {path}"
        )

        return False

    # ------------------------------------------------------
    # Remember existing VS Code windows
    # ------------------------------------------------------

    before_handles = set()

    for window in get_vscode_windows():

        try:
            before_handles.add(
                window._hWnd
            )
        except Exception:
            pass

    # ------------------------------------------------------
    # Open a NEW VS Code window
    # ------------------------------------------------------

    try:

        print(
            "Starting new tracked VS Code window..."
        )

        print(
            f"VS Code executable: {path}"
        )

        subprocess.Popen(
            [
                path,
                "--new-window",
            ],
            shell=False
        )

    except Exception as error:

        print(
            "VS Code launch error:",
            error
        )

        return False

    # ------------------------------------------------------
    # Wait for the new VS Code window
    # ------------------------------------------------------

    for _ in range(30):

        time.sleep(0.5)

        current_windows = get_vscode_windows()

        for window in current_windows:

            try:

                handle = window._hWnd

                if handle not in before_handles:

                    tracked_vscode_window = window

                    print(
                        "VS Code window opened."
                    )

                    print(
                        f"Tracked VS Code window: "
                        f"{handle}"
                    )

                    print(
                        f"Window title: "
                        f"{window.title}"
                    )

                    return True

            except Exception:

                continue

    # ------------------------------------------------------
    # New window could not be identified
    # ------------------------------------------------------

    print(
        "VS Code opened but the new window "
        "could not be tracked."
    )

    return False


def close_tracked_vscode():
    """
    Close ONLY the VS Code window that
    Aria opened and is currently tracking.
    """

    global tracked_vscode_window

    if tracked_vscode_window is None:

        print(
            "No VS Code window is currently "
            "tracked by Aria."
        )

        return False

    try:

        window = tracked_vscode_window

        handle = window._hWnd

        print(
            "Closing tracked VS Code window..."
        )

        print(
            f"Window handle: {handle}"
        )

        print(
            f"Window title: {window.title}"
        )

        # --------------------------------------------------
        # Restore if minimized
        # --------------------------------------------------

        try:

            if window.isMinimized:

                window.restore()

                time.sleep(0.3)

        except Exception:

            pass

        # --------------------------------------------------
        # Close ONLY this window
        # --------------------------------------------------

        window.close()

        time.sleep(1)

        # --------------------------------------------------
        # Check whether exact window closed
        # --------------------------------------------------

        remaining_handles = set()

        for current_window in get_vscode_windows():

            try:

                remaining_handles.add(
                    current_window._hWnd
                )

            except Exception:

                pass

        if handle not in remaining_handles:

            print(
                "Tracked VS Code window "
                "closed successfully."
            )

            tracked_vscode_window = None

            return True

        print(
            "Tracked VS Code window "
            "is still open."
        )

        return False

    except Exception as error:

        print(
            "Tracked VS Code close error:",
            error
        )

        return False


# ==========================================================
# APPLICATION ALIASES
# ==========================================================

ALIASES = {

    # ------------------------------------------------------
    # VISUAL STUDIO CODE
    # ------------------------------------------------------

    "vscode": [
        "vscode",
        "vs code",
        "vs-code",
        "visual studio code",
        "code",
        "code.exe",
    ],

    "vs code": [
        "vscode",
        "vs code",
        "vs-code",
        "visual studio code",
        "code",
        "code.exe",
    ],

    "vs-code": [
        "vscode",
        "vs code",
        "visual studio code",
        "code",
        "code.exe",
    ],

    "visual studio code": [
        "vscode",
        "vs code",
        "visual studio code",
        "code",
        "code.exe",
    ],

    "code": [
        "vscode",
        "vs code",
        "visual studio code",
        "code",
        "code.exe",
    ],

    # ------------------------------------------------------
    # CHROME
    # ------------------------------------------------------

    "chrome": [
        "google chrome",
        "chrome",
        "chrome.exe",
    ],

    "google chrome": [
        "google chrome",
        "chrome",
        "chrome.exe",
    ],

    # ------------------------------------------------------
    # EDGE
    # ------------------------------------------------------

    "edge": [
        "microsoft edge",
        "edge",
        "msedge",
        "msedge.exe",
    ],

    "microsoft edge": [
        "microsoft edge",
        "edge",
        "msedge",
        "msedge.exe",
    ],

    # ------------------------------------------------------
    # NOTEPAD
    # ------------------------------------------------------

    "notepad": [
        "notepad",
        "notepad.exe",
    ],

    # ------------------------------------------------------
    # CALCULATOR
    # ------------------------------------------------------

    "calculator": [
        "calculator",
        "windows calculator",
        "calc",
        "calc.exe",
    ],

    "calc": [
        "calculator",
        "windows calculator",
        "calc",
        "calc.exe",
    ],

    # ------------------------------------------------------
    # FILE EXPLORER
    # ------------------------------------------------------

    "explorer": [
        "file explorer",
        "explorer",
        "windows explorer",
        "explorer.exe",
    ],

    "file explorer": [
        "file explorer",
        "explorer",
        "windows explorer",
        "explorer.exe",
    ],

    # ------------------------------------------------------
    # TERMINAL
    # ------------------------------------------------------

    "terminal": [
        "windows terminal",
        "terminal",
        "wt",
        "wt.exe",
    ],

    # ------------------------------------------------------
    # COMMAND PROMPT
    # ------------------------------------------------------

    "cmd": [
        "command prompt",
        "cmd",
        "cmd.exe",
    ],

    "command prompt": [
        "command prompt",
        "cmd",
        "cmd.exe",
    ],

    # ------------------------------------------------------
    # POWERSHELL
    # ------------------------------------------------------

    "powershell": [
        "powershell",
        "windows powershell",
        "powershell.exe",
    ],

    "windows powershell": [
        "powershell",
        "windows powershell",
        "powershell.exe",
    ],
}


# ==========================================================
# NORMALIZE TEXT
# ==========================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower().strip()

    text = text.replace(
        "_",
        " "
    )

    text = text.replace(
        "-",
        " "
    )

    text = re.sub(
        r"\.(exe|lnk|url)$",
        "",
        text
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.strip()

    # ------------------------------------------------------
    # Normalize VS Code speech variations
    # ------------------------------------------------------

    compact = text.replace(
        " ",
        ""
    )

    if compact in {
        "vscode",
        "visualstudiocode",
    }:

        return "vscode"

    return text


# ==========================================================
# SIMILARITY
# ==========================================================

def similarity(a, b):

    a = normalize_text(a)
    b = normalize_text(b)

    if not a or not b:
        return 0.0

    if a == b:
        return 1.0

    if a in b or b in a:
        return 0.95

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


# ==========================================================
# GET ALIASES
# ==========================================================

def get_aliases(query):

    query = normalize_text(
        query
    )

    aliases = [
        query
    ]

    if query in ALIASES:

        aliases.extend(
            ALIASES[query]
        )

    for key, values in ALIASES.items():

        if query == normalize_text(key):

            aliases.extend(
                values
            )

    cleaned = []

    for item in aliases:

        item = normalize_text(
            item
        )

        if item and item not in cleaned:

            cleaned.append(item)

    return cleaned


# ==========================================================
# WINDOWS START MENU APPLICATIONS
# ==========================================================

def get_start_menu_apps():

    apps = []

    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        (
            "Get-StartApps | "
            "ForEach-Object { "
            "$_.Name + '||' + $_.AppID "
            "}"
        ),
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

        if result.returncode != 0:
            return apps

        for line in result.stdout.splitlines():

            if "||" not in line:
                continue

            name, app_id = line.split(
                "||",
                1
            )

            name = name.strip()
            app_id = app_id.strip()

            if not name or not app_id:
                continue

            apps.append(
                {
                    "name": name,
                    "app_id": app_id,
                    "type": "start_menu",
                }
            )

    except Exception as error:

        print(
            "Start Menu discovery error:",
            error
        )

    return apps


# ==========================================================
# FIND EXECUTABLE ON PATH
# ==========================================================

def find_executable_on_path(name):

    names = [
        name
    ]

    if not name.lower().endswith(
        ".exe"
    ):

        names.append(
            name + ".exe"
        )

    for candidate in names:

        try:

            result = subprocess.run(
                [
                    "where",
                    candidate
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )

            if result.returncode == 0:

                paths = (
                    result.stdout
                    .strip()
                    .splitlines()
                )

                for path in paths:

                    path = path.strip()

                    # Only return actual EXE files.
                    if (
                        path.lower().endswith(".exe")
                        and os.path.isfile(path)
                    ):

                        return path

        except Exception:

            pass

    return None


# ==========================================================
# SPECIAL VS CODE DETECTION
# ==========================================================

def find_vscode():

    # ------------------------------------------------------
    # IMPORTANT:
    # Do NOT trust "where code" first because Windows may
    # return code.cmd from the VS Code bin folder.
    # ------------------------------------------------------

    local_app_data = os.environ.get(
        "LOCALAPPDATA",
        ""
    )

    program_files = os.environ.get(
        "PROGRAMFILES",
        ""
    )

    program_files_x86 = os.environ.get(
        "PROGRAMFILES(X86)",
        ""
    )

    possible_paths = []

    # ------------------------------------------------------
    # 1. USER INSTALLATION
    # ------------------------------------------------------

    if local_app_data:

        possible_paths.append(
            os.path.join(
                local_app_data,
                "Programs",
                "Microsoft VS Code",
                "Code.exe",
            )
        )

    # ------------------------------------------------------
    # 2. SYSTEM INSTALLATION
    # ------------------------------------------------------

    if program_files:

        possible_paths.append(
            os.path.join(
                program_files,
                "Microsoft VS Code",
                "Code.exe",
            )
        )

    # ------------------------------------------------------
    # 3. 32-BIT INSTALLATION
    # ------------------------------------------------------

    if program_files_x86:

        possible_paths.append(
            os.path.join(
                program_files_x86,
                "Microsoft VS Code",
                "Code.exe",
            )
        )

    # ------------------------------------------------------
    # Check known locations
    # ------------------------------------------------------

    checked = set()

    for path in possible_paths:

        if not path:
            continue

        normalized = os.path.normpath(
            path
        ).lower()

        if normalized in checked:
            continue

        checked.add(
            normalized
        )

        if (
            path.lower().endswith("code.exe")
            and os.path.isfile(path)
        ):

            return path

    # ------------------------------------------------------
    # 4. PATH FALLBACK
    # ------------------------------------------------------

    code_path = find_executable_on_path(
        "Code.exe"
    )

    if code_path:

        return code_path

    return None


# ==========================================================
# FIND COMMON APPLICATION PATHS
# ==========================================================

def find_common_application_paths(query):

    aliases = get_aliases(
        query
    )

    results = []

    normalized_query = normalize_text(
        query
    )

    # ------------------------------------------------------
    # SPECIAL CASE: VS CODE
    # ------------------------------------------------------

    if normalized_query == "vscode":

        vscode_path = find_vscode()

        if vscode_path:

            results.append(
                {
                    "name": "Visual Studio Code",
                    "path": vscode_path,
                    "type": "vscode",
                    "score": 1.0,
                }
            )

    # ------------------------------------------------------
    # NORMAL APPLICATION PATHS
    # ------------------------------------------------------

    roots = []

    local_appdata = os.environ.get(
        "LOCALAPPDATA",
        ""
    )

    program_files = os.environ.get(
        "PROGRAMFILES",
        ""
    )

    program_files_x86 = os.environ.get(
        "PROGRAMFILES(X86)",
        ""
    )

    if local_appdata:
        roots.append(
            Path(local_appdata) / "Programs"
        )

    if program_files:
        roots.append(
            Path(program_files)
        )

    if program_files_x86:
        roots.append(
            Path(program_files_x86)
        )

    for root in roots:

        if not root.exists():
            continue

        for alias in aliases:

            normalized_alias = normalize_text(
                alias
            )

            if not normalized_alias:
                continue

            try:

                for path in root.glob(
                    "**/*.exe"
                ):

                    name = normalize_text(
                        path.stem
                    )

                    if (
                        normalized_alias == name
                        or normalized_alias in name
                        or name in normalized_alias
                    ):

                        results.append(
                            {
                                "name": path.stem,
                                "path": str(path),
                                "type": "executable",
                                "score": similarity(
                                    normalized_alias,
                                    name
                                ),
                            }
                        )

            except Exception:

                continue

    return results


# ==========================================================
# SEARCH APPLICATIONS
# ==========================================================

def search_applications(query):

    original_query = query

    query = normalize_text(
        query
    )

    if not query:
        return []

    results = []

    # ------------------------------------------------------
    # SPECIAL VS CODE HANDLING
    # ------------------------------------------------------

    if query == "vscode":

        vscode_path = find_vscode()

        if vscode_path:

            results.append(
                {
                    "name": "Visual Studio Code",
                    "path": vscode_path,
                    "type": "vscode",
                    "score": 1.0,
                }
            )

    # ------------------------------------------------------
    # ALIASES
    # ------------------------------------------------------

    aliases = get_aliases(
        original_query
    )

    # ------------------------------------------------------
    # START MENU
    # ------------------------------------------------------

    apps = get_start_menu_apps()

    for app in apps:

        app_name = normalize_text(
            app["name"]
        )

        score = 0

        for alias in aliases:

            score = max(
                score,
                similarity(
                    alias,
                    app_name
                )
            )

        # --------------------------------------------------
        # Extra VS Code matching
        # --------------------------------------------------

        if query == "vscode":

            if (
                "visual studio code"
                in app_name
                or app_name == "code"
                or "vs code"
                in app_name
            ):

                score = 1.0

        if score >= 0.60:

            result = dict(app)

            result["score"] = score

            results.append(
                result
            )

    # ------------------------------------------------------
    # PATH EXECUTABLE
    # ------------------------------------------------------

    executable = find_executable_on_path(
        query
    )

    if executable:

        results.append(
            {
                "name": Path(
                    executable
                ).stem,

                "path": executable,

                "type": "path",

                "score": 1.0,
            }
        )

    # ------------------------------------------------------
    # COMMON INSTALLATION PATHS
    # ------------------------------------------------------

    results.extend(
        find_common_application_paths(
            original_query
        )
    )

    # ------------------------------------------------------
    # REMOVE DUPLICATES
    # ------------------------------------------------------

    unique = {}

    for result in results:

        identifier = (
            result.get("app_id")
            or result.get("path")
            or result.get("name")
        )

        identifier = str(
            identifier
        ).lower()

        if identifier not in unique:

            unique[
                identifier
            ] = result

        else:

            existing = unique[
                identifier
            ]

            if (
                result.get("score", 0)
                >
                existing.get("score", 0)
            ):

                unique[
                    identifier
                ] = result

    results = list(
        unique.values()
    )

    # ------------------------------------------------------
    # SORT
    # ------------------------------------------------------

    results.sort(
        key=lambda item: item.get(
            "score",
            0
        ),
        reverse=True
    )

    return results


# ==========================================================
# OPEN APPLICATION
# ==========================================================

def open_application(query):

    results = search_applications(
        query
    )

    if not results:

        return {
            "success": False,
            "response": (
                f"I couldn't find {query} "
                "on your computer."
            ),
        }

    best = results[0]

    # ------------------------------------------------------
    # VS CODE
    # ------------------------------------------------------

    if best.get("type") == "vscode":

        path = best.get(
            "path"
        )

        if path and os.path.exists(path):

            success = open_tracked_vscode(
                path
            )

            if success:

                return {
                    "success": True,
                    "name": "Visual Studio Code",
                    "response": (
                        "Opening Visual Studio Code."
                    ),
                }

            return {
                "success": False,
                "response": (
                    "I found Visual Studio Code "
                    "but couldn't track its window."
                ),
            }

    # ------------------------------------------------------
    # START MENU APPLICATION
    # ------------------------------------------------------

    if best.get("type") == "start_menu":

        app_id = best.get(
            "app_id"
        )

        if app_id:

            try:

                subprocess.Popen(
                    [
                        "explorer.exe",
                        f"shell:AppsFolder\\{app_id}",
                    ]
                )

                return {
                    "success": True,
                    "name": best["name"],
                    "response": (
                        f"Opening {best['name']}."
                    ),
                }

            except Exception as error:

                print(
                    "Start Menu launch error:",
                    error
                )

    # ------------------------------------------------------
    # NORMAL EXECUTABLE
    # ------------------------------------------------------

    path = best.get(
        "path"
    )

    if path and os.path.exists(path):

        try:

            subprocess.Popen(
                [
                    path
                ],
                shell=False
            )

            return {
                "success": True,
                "name": best["name"],
                "response": (
                    f"Opening {best['name']}."
                ),
            }

        except Exception as error:

            print(
                "Executable launch error:",
                error
            )

    # ------------------------------------------------------
    # WINDOWS FALLBACK
    # ------------------------------------------------------

    try:

        os.startfile(
            best.get(
                "path"
            )
            or best["name"]
        )

        return {
            "success": True,
            "name": best["name"],
            "response": (
                f"Opening {best['name']}."
            ),
        }

    except Exception as error:

        print(
            "Application fallback error:",
            error
        )

    return {
        "success": False,
        "response": (
            f"I found {best['name']} "
            "but couldn't open it."
        ),
    }


# ==========================================================
# FOLDER SEARCH
# ==========================================================

def search_folders(query):

    query = normalize_text(
        query
    )

    if not query:
        return []

    results = []

    for root in FOLDER_SEARCH_PATHS:

        if not root.exists():
            continue

        try:

            for path in root.rglob("*"):

                if not path.is_dir():
                    continue

                name = normalize_text(
                    path.name
                )

                if not name:
                    continue

                score = similarity(
                    query,
                    name
                )

                if query in name:

                    score = max(
                        score,
                        0.95
                    )

                if score >= 0.60:

                    results.append(
                        {
                            "name": path.name,
                            "path": str(path),
                            "type": "folder",
                            "score": score,
                        }
                    )

        except Exception:

            continue

    results.sort(
        key=lambda item: item[
            "score"
        ],
        reverse=True
    )

    return results


# ==========================================================
# COMPUTER SEARCH
# ==========================================================

def search_computer(query):

    application_results = (
        search_applications(
            query
        )
    )

    folder_results = (
        search_folders(
            query
        )
    )

    return {
        "applications": application_results,
        "folders": folder_results,
    }


# ==========================================================
# OPEN SEARCH RESULT
# ==========================================================

def open_search_result(result):

    if not result:
        return False

    result_type = result.get(
        "type"
    )

    # ------------------------------------------------------
    # VISUAL STUDIO CODE
    # ------------------------------------------------------

    if result_type == "vscode":

        path = result.get(
            "path"
        )

        if not path:
            return False

        return open_tracked_vscode(
            path
        )

    # ------------------------------------------------------
    # START MENU
    # ------------------------------------------------------

    if result_type == "start_menu":

        app_id = result.get(
            "app_id"
        )

        if not app_id:
            return False

        try:

            subprocess.Popen(
                [
                    "explorer.exe",
                    f"shell:AppsFolder\\{app_id}",
                ]
            )

            return True

        except Exception as error:

            print(
                "Could not open Start Menu app:",
                error
            )

            return False

    # ------------------------------------------------------
    # PATH / EXECUTABLE
    # ------------------------------------------------------

    path = result.get(
        "path"
    )

    if not path:
        return False

    if not os.path.exists(path):
        return False

    try:

        os.startfile(
            path
        )

        return True

    except Exception as error:

        print(
            "Could not open search result:",
            error
        )

        return False


# ==========================================================
# BEST APPLICATION
# ==========================================================

def find_best_application(query):

    results = search_applications(
        query
    )

    if not results:
        return None

    return results[0]


# ==========================================================
# BEST FOLDER
# ==========================================================

def find_best_folder(query):

    results = search_folders(
        query
    )

    if not results:
        return None

    return results[0]


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print()
    print("=" * 55)
    print("       ARIA COMPUTER SEARCH TEST")
    print("=" * 55)
    print()

    print(
        "VS Code executable:"
    )

    print(
        find_vscode()
    )

    print()

    test_queries = [
        "vscode",
        "vs code",
        "visual studio code",
        "code",
        "chrome",
        "notepad",
        "calculator",
    ]

    for query in test_queries:

        print()
        print(
            f"Searching for: {query}"
        )

        print(
            "-" * 45
        )

        results = search_applications(
            query
        )

        if not results:

            print(
                "No application found."
            )

            continue

        for result in results[:5]:

            print(
                f"Name: {result.get('name')}"
            )

            print(
                f"Type: {result.get('type')}"
            )

            if result.get("path"):

                print(
                    f"Path: {result.get('path')}"
                )

            if result.get("app_id"):

                print(
                    f"App ID: {result.get('app_id')}"
                )

            print(
                f"Score: {result.get('score', 0):.2f}"
            )

            print()