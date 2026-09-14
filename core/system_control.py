import os
import subprocess
import webbrowser
from pathlib import Path


HOME = Path.home()

DOWNLOADS = HOME / "Downloads"
DOCUMENTS = HOME / "Documents"
DESKTOP = HOME / "Desktop"


# --------------------------------------------------
# OPEN APPLICATION
# --------------------------------------------------

def open_application(application: str) -> bool:
    if not application:
        return False

    application = application.lower().strip()

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
        "vscode": [
            "cmd",
            "/c",
            "start",
            "",
            "code",
        ],
        "visual studio code": [
            "cmd",
            "/c",
            "start",
            "",
            "code",
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

    command = applications.get(application)

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


# --------------------------------------------------
# CLOSE APPLICATION
# --------------------------------------------------

def close_application(application: str) -> bool:
    if not application:
        return False

    application = application.lower().strip()

    # Common names → actual Windows process names
    aliases = {
        "chrome": "chrome",
        "google chrome": "chrome",
        "chrome browser": "chrome",

        "edge": "msedge",
        "microsoft edge": "msedge",

        "firefox": "firefox",

        "vscode": "code",
        "visual studio code": "code",
        "vs code": "code",

        "notepad": "notepad",

        "calculator": "calculator",
        "calc": "calculator",
    }

    process_name = aliases.get(
        application,
        application,
    )

    # Processes Aria should NEVER terminate
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

        # taskkill returns 0 when the process
        # was successfully terminated
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


# --------------------------------------------------
# OPEN WEBSITE
# --------------------------------------------------

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
        webbrowser.open(url)

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


# --------------------------------------------------
# OPEN FOLDER
# --------------------------------------------------

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

    path = folders.get(folder)

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


# --------------------------------------------------
# WEB SEARCH
# --------------------------------------------------

def search_web(query: str) -> bool:
    if not query:
        return False

    query = query.strip()

    if not query:
        return False

    try:

        search_url = (
            "https://www.google.com/search?q="
            + query.replace(" ", "+")
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


# --------------------------------------------------
# TEST
# --------------------------------------------------

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