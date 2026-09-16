import os
import subprocess
import webbrowser
from pathlib import Path

from commands.computer_search import (
    open_tracked_vscode,
    close_tracked_vscode,
    find_vscode,
)


HOME = Path.home()

DOWNLOADS = HOME / "Downloads"
DOCUMENTS = HOME / "Documents"
DESKTOP = HOME / "Desktop"


# ==========================================================
# OPEN APPLICATION
# ==========================================================

def open_application(application: str) -> bool:

    if not application:
        return False

    application = application.lower().strip()

    # ------------------------------------------------------
    # VS CODE
    # ------------------------------------------------------

    vscode_names = {
        "vscode",
        "vs code",
        "vs-code",
        "visual studio code",
        "code",
    }

    if application in vscode_names:

        vscode_path = find_vscode()

        if not vscode_path:

            print(
                "Visual Studio Code executable "
                "was not found."
            )

            return False

        success = open_tracked_vscode(
            vscode_path
        )

        if success:

            print(
                "Opened and tracked "
                "Visual Studio Code."
            )

            return True

        print(
            "VS Code opened but could not "
            "be tracked."
        )

        return False

    # ------------------------------------------------------
    # OTHER APPLICATIONS
    # ------------------------------------------------------

    applications = {

        "chrome": [
            "cmd",
            "/c",
            "start",
            "",
            "chrome",
        ],

        "google chrome": [
            "cmd",
            "/c",
            "start",
            "",
            "chrome",
        ],

        "chrome browser": [
            "cmd",
            "/c",
            "start",
            "",
            "chrome",
        ],

        "file explorer": [
            "explorer",
        ],

        "explorer": [
            "explorer",
        ],

        "notepad": [
            "notepad.exe",
        ],

        "calculator": [
            "calc.exe",
        ],
    }

    command = applications.get(
        application
    )

    if not command:

        return False

    try:

        subprocess.Popen(
            command,
            shell=False,
        )

        print(
            f"Opened application: "
            f"{application}"
        )

        return True

    except Exception as e:

        print(
            f"Failed to open "
            f"{application}:",
            e,
        )

        return False


# ==========================================================
# CLOSE APPLICATION
# ==========================================================

def close_application(application: str) -> bool:

    if not application:
        return False

    application = application.lower().strip()

    # ------------------------------------------------------
    # VS CODE
    #
    # IMPORTANT:
    # NEVER use taskkill for VS Code.
    #
    # We close only the exact VS Code window
    # that Aria opened and is tracking.
    # ------------------------------------------------------

    vscode_names = {
        "vscode",
        "vs code",
        "vs-code",
        "visual studio code",
        "code",
    }

    if application in vscode_names:

        print(
            "VS Code close requested."
        )

        success = close_tracked_vscode()

        if success:

            print(
                "Closed only the tracked "
                "VS Code window."
            )

            return True

        print(
            "Could not close the tracked "
            "VS Code window."
        )

        return False

    # ------------------------------------------------------
    # NORMAL APPLICATION CLOSE
    # ------------------------------------------------------

    aliases = {

        "chrome": "chrome",
        "google chrome": "chrome",
        "chrome browser": "chrome",

        "edge": "msedge",
        "microsoft edge": "msedge",

        "firefox": "firefox",

        "notepad": "notepad",

        "calculator": "calculator",
        "calc": "calculator",
    }

    process_name = aliases.get(
        application,
        application,
    )

    # ------------------------------------------------------
    # PROTECTED PROCESSES
    # ------------------------------------------------------

    protected_processes = {

        "explorer",
        "explorer.exe",

        "dwm",
        "dwm.exe",

        "winlogon",
        "winlogon.exe",

        "csrss",
        "csrss.exe",

        "lsass",
        "lsass.exe",

        "services",
        "services.exe",

        "svchost",
        "svchost.exe",

        "system",
        "system.exe",
    }

    if process_name in protected_processes:

        print(
            f"Blocked attempt to close "
            f"protected process: "
            f"{process_name}"
        )

        return False

    # ------------------------------------------------------
    # CLOSE NORMAL APPLICATION
    # ------------------------------------------------------

    try:

        command = [
            "taskkill",
            "/IM",
            f"{process_name}.exe",
            "/F",
        ]

        print(
            "Close command:",
            " ".join(command),
        )

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.stdout:

            print(
                result.stdout.strip()
            )

        if result.stderr:

            print(
                result.stderr.strip()
            )

        if result.returncode == 0:

            print(
                f"Closed application: "
                f"{application}"
            )

            return True

        print(
            f"Could not close "
            f"{application}."
        )

        return False

    except (
        OSError,
        subprocess.SubprocessError,
    ) as e:

        print(
            "Failed to close application:",
            e,
        )

        return False


# ==========================================================
# OPEN WEBSITE
# ==========================================================

def open_website(url: str) -> bool:

    if not url:

        return False

    url = url.strip()

    if not url.startswith(
        (
            "http://",
            "https://",
        )
    ):

        url = "https://" + url

    try:

        webbrowser.open(
            url
        )

        print(
            f"Opened website: {url}"
        )

        return True

    except Exception as e:

        print(
            "Failed to open website:",
            e,
        )

        return False


# ==========================================================
# OPEN FOLDER
# ==========================================================

def open_folder(folder: str) -> bool:

    if not folder:

        return False

    folder = folder.lower().strip()

    folders = {

        "downloads": DOWNLOADS,
        "download": DOWNLOADS,

        "documents": DOCUMENTS,
        "document": DOCUMENTS,

        "desktop": DESKTOP,
        "desktop folder": DESKTOP,
    }

    path = folders.get(
        folder
    )

    if not path:

        return False

    if not path.exists():

        print(
            f"Folder does not exist: "
            f"{path}"
        )

        return False

    try:

        os.startfile(
            str(path)
        )

        print(
            f"Opened folder: {path}"
        )

        return True

    except Exception as e:

        print(
            "Failed to open folder:",
            e,
        )

        return False


# ==========================================================
# WEB SEARCH
# ==========================================================

def search_web(query: str) -> bool:

    if not query:

        return False

    query = query.strip()

    if not query:

        return False

    try:

        search_url = (
            "https://www.google.com/search?q="
            + query.replace(
                " ",
                "+"
            )
        )

        webbrowser.open(
            search_url
        )

        print(
            f"Searching web for: "
            f"{query}"
        )

        return True

    except Exception as e:

        print(
            "Failed to search web:",
            e,
        )

        return False


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "Aria System Control Module"
    )

    print(
        "--------------------------"
    )

    print(
        "System control module loaded."
    )