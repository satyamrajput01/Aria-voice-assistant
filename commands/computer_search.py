import os
import subprocess
from pathlib import Path
from difflib import SequenceMatcher


HOME = Path.home()


START_MENU_LOCATIONS = [
    Path(
        os.environ.get(
            "ProgramData",
            "C:\\ProgramData",
        )
    )
    / "Microsoft"
    / "Windows"
    / "Start Menu",

    HOME
    / "AppData"
    / "Roaming"
    / "Microsoft"
    / "Windows"
    / "Start Menu",
]


FOLDER_SEARCH_LOCATIONS = [
    HOME / "Desktop",
    HOME / "Downloads",
    HOME / "Documents",
]


IGNORED_APPLICATION_WORDS = {
    "setup",
    "installer",
    "install",
    "uninstall",
    "manual",
    "documentation",
    "readme",
    "config",
    "share",
    "license",
    "help",
    "repair",
    "update",
}


def normalize_text(text: str) -> str:
    """
    Normalize text so application names can be
    compared more reliably.
    """

    if not text:
        return ""

    text = text.lower().strip()

    replacements = {
        "-": " ",
        "_": " ",
        "(": " ",
        ")": " ",
        "[": " ",
        "]": " ",
        ".": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(text.split())


def similarity(query: str, name: str) -> float:
    """
    Calculate relevance between a search query
    and an application or folder name.
    """

    query = normalize_text(query)
    name = normalize_text(name)

    if not query or not name:
        return 0.0

    # Exact name match.
    if query == name:
        return 1.0

    query_words = query.split()
    name_words = name.split()

    # Count complete word matches.
    matched_words = 0

    for word in query_words:
        if word in name_words:
            matched_words += 1

    if query_words:
        word_score = matched_words / len(query_words)
    else:
        word_score = 0.0

    # Complete query appears inside the name.
    if query in name:
        phrase_score = 0.95
    else:
        phrase_score = 0.0

    # Fuzzy similarity.
    fuzzy_score = SequenceMatcher(
        None,
        query,
        name,
    ).ratio()

    fuzzy_score *= 0.75

    return max(
        word_score,
        phrase_score,
        fuzzy_score,
    )


def is_ignored_application_name(
    name: str,
) -> bool:
    """
    Ignore installers, uninstallers, manuals
    and other non-useful application entries.
    """

    normalized = normalize_text(name)

    words = set(
        normalized.split()
    )

    for ignored_word in IGNORED_APPLICATION_WORDS:

        if ignored_word in words:
            return True

    return False


def get_windows_applications():
    """
    Get applications known to Windows through
    PowerShell Get-StartApps.

    This includes many Microsoft Store and
    Windows applications that do not have normal
    .lnk files.
    """

    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "Get-StartApps | "
            "ForEach-Object { "
            "$_.Name + '|||' + $_.AppID "
            "}"
        ),
    ]

    try:

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

    except (
        subprocess.SubprocessError,
        OSError,
    ):
        return []

    if process.returncode != 0:
        return []

    results = []

    for line in process.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        if "|||" not in line:
            continue

        name, app_id = line.split(
            "|||",
            1,
        )

        name = name.strip()
        app_id = app_id.strip()

        if not name or not app_id:
            continue

        if is_ignored_application_name(
            name
        ):
            continue

        results.append(
            {
                "name": name,
                "path": app_id,
                "app_id": app_id,
                "score": 0.0,
                "type": "windows_application",
            }
        )

    return results


def search_start_menu_applications(
    query: str,
):
    """
    Search normal Windows Start Menu
    application shortcuts.
    """

    results = []

    for location in START_MENU_LOCATIONS:

        if not location.exists():
            continue

        try:

            for path in location.rglob("*"):

                if not path.is_file():
                    continue

                if path.suffix.lower() not in {
                    ".lnk",
                    ".appref-ms",
                }:
                    continue

                name = path.stem

                if is_ignored_application_name(
                    name
                ):
                    continue

                score = similarity(
                    query,
                    name,
                )

                if score < 0.65:
                    continue

                results.append(
                    {
                        "name": name,
                        "path": str(path),
                        "score": score,
                        "type": "application",
                    }
                )

        except (
            PermissionError,
            OSError,
        ):
            continue

    return results


def search_applications(
    query: str,
    limit: int = 10,
):
    """
    Search both Windows applications and
    normal desktop applications.
    """

    if not query:
        return []

    query = query.strip()

    results = []

    # -------------------------------------------------
    # Search Windows application database
    # -------------------------------------------------

    windows_apps = get_windows_applications()

    for app in windows_apps:

        score = similarity(
            query,
            app["name"],
        )

        if score < 0.65:
            continue

        app["score"] = score

        results.append(app)

    # -------------------------------------------------
    # Search normal Start Menu shortcuts
    # -------------------------------------------------

    start_menu_apps = (
        search_start_menu_applications(
            query
        )
    )

    results.extend(
        start_menu_apps
    )

    # -------------------------------------------------
    # Sort by relevance
    # -------------------------------------------------

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    # -------------------------------------------------
    # Remove duplicate applications
    #
    # Example:
    #
    # Visual Studio Code
    # Visual Studio Code
    #
    # becomes one result.
    # -------------------------------------------------

    unique_results = []

    seen_names = set()

    for result in results:

        normalized_name = normalize_text(
            result["name"]
        )

        if normalized_name in seen_names:
            continue

        seen_names.add(
            normalized_name
        )

        unique_results.append(
            result
        )

    return unique_results[:limit]


def search_folders(
    query: str,
    limit: int = 10,
):
    """
    Search Desktop, Downloads and Documents
    for folders matching the query.
    """

    if not query:
        return []

    query = query.strip()

    results = []

    for location in FOLDER_SEARCH_LOCATIONS:

        if not location.exists():
            continue

        try:

            for path in location.rglob("*"):

                if not path.is_dir():
                    continue

                name = path.name

                score = similarity(
                    query,
                    name,
                )

                if score < 0.65:
                    continue

                results.append(
                    {
                        "name": name,
                        "path": str(path),
                        "score": score,
                        "type": "folder",
                    }
                )

        except (
            PermissionError,
            OSError,
        ):
            continue

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    unique_results = []

    seen_paths = set()

    for result in results:

        path = result["path"].lower()

        if path in seen_paths:
            continue

        seen_paths.add(path)

        unique_results.append(
            result
        )

    return unique_results[:limit]


def search_computer(
    query: str,
    item_type: str = "application",
):
    """
    General computer search.

    item_type:
        application
        folder
    """

    if item_type == "folder":
        return search_folders(query)

    return search_applications(query)


def open_search_result(
    result: dict,
) -> bool:
    """
    Open a result returned by the computer
    search system.
    """

    if not result:
        return False

    result_type = result.get(
        "type"
    )

    # -------------------------------------------------
    # Windows application
    # -------------------------------------------------

    if result_type == "windows_application":

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
                ],
                shell=False,
            )

            return True

        except (
            OSError,
            FileNotFoundError,
        ):
            return False

    # -------------------------------------------------
    # Normal application or folder
    # -------------------------------------------------

    path = result.get(
        "path"
    )

    if not path:
        return False

    try:

        os.startfile(path)

        return True

    except (
        OSError,
        FileNotFoundError,
    ):
        return False


if __name__ == "__main__":

    print("Computer Search Test")
    print("--------------------")

    query = input(
        "Application to search: "
    ).strip()

    results = search_applications(
        query
    )

    print()

    if not results:

        print(
            "No matching applications found."
        )

    else:

        print(
            "Matching applications:"
        )

        for index, result in enumerate(
            results,
            start=1,
        ):

            print(
                f"{index}. "
                f"{result['name']} "
                f"({result['score']:.2f})"
            )

            if result["type"] == (
                "windows_application"
            ):

                print(
                    f"   Windows App ID: "
                    f"{result['app_id']}"
                )

            else:

                print(
                    f"   {result['path']}"
                )