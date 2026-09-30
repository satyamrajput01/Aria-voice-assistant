import re

from commands.web_control import (
    open_website as open_web_website,
    google_search,
    youtube_search,
)

from commands.computer_search import (
    search_applications,
    open_search_result,
    close_application,
)

from commands.chrome_control import (
    get_chrome_profiles,
    find_profile_by_alias,
    open_managed_chrome_profile,
    close_managed_chrome_profile,
)

from commands.file_control import (
    open_folder,
    create_folder,
    delete_folder,
    find_custom_folder,
)


# ============================================================
# STATE
# ============================================================

pending_app_results = []
pending_chrome_profiles = []
pending_folder_deletion = None


# ============================================================
# APPLICATION ALIASES
# ============================================================

APP_ALIASES = {
    "vscode": [
        "visual studio code",
        "code",
        "vs code",
        "vs-code",
    ],

    "vs code": [
        "visual studio code",
        "vscode",
        "code",
        "vs-code",
    ],

    "vs-code": [
        "visual studio code",
        "vscode",
        "code",
        "vs code",
    ],

    "code": [
        "visual studio code",
        "code",
    ],

    "visual studio code": [
        "visual studio code",
        "vscode",
        "vs code",
        "vs-code",
        "code",
    ],

    "chrome": [
        "google chrome",
        "chrome",
    ],

    "google chrome": [
        "google chrome",
        "chrome",
    ],

    "notepad": [
        "notepad",
    ],

    "calculator": [
        "calculator",
    ],

    "calc": [
        "calculator",
    ],

    "explorer": [
        "file explorer",
        "explorer",
    ],

    "file explorer": [
        "file explorer",
        "explorer",
    ],
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(text):

    if not text:
        return ""

    text = text.lower().strip()

    text = text.replace("-", " ")

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# WEBSITE HELPERS
# ============================================================

def open_website(name):

    name = normalize(name)

    url = WEBSITE_ALIASES.get(name)

    if not url:
        return False

    try:
        webbrowser.open(url)
        return True

    except Exception as error:
        print(
            f"Website opening error: {error}"
        )
        return False


def is_known_website(name):

    return normalize(name) in WEBSITE_ALIASES


# ============================================================
# WEBSITE OPEN
# ============================================================

def handle_website_open(command):

    text = normalize(command)

    if not text.startswith("open "):
        return None

    target = text[5:].strip()

    if not target:
        return None

    result = open_web_website(target)

    if not result.get("success"):
        return None

    return {
        "handled": True,
        "action": "open_website",
        "target": target,
        "url": result.get("url"),
        "response": result.get(
            "response",
            f"Opening {target}."
        ),
    }


# ============================================================
# WEB SEARCH
# ============================================================

def handle_web_search(command):

    text = normalize(command)

    google_match = re.match(
        r"^search\s+google\s+(?:for\s+)?(.+)$",
        text,
    )

    if google_match:
        query = google_match.group(1).strip()
        result = google_search(query)
        return {
            "handled": True,
            "action": "web_search" if result.get("success") else "search_failed",
            "target": query,
            "engine": "google",
            "response": result.get("response", "I couldn't perform that search."),
        }

    youtube_match = re.match(
        r"^search\s+youtube\s+(?:for\s+)?(.+)$",
        text,
    )

    if youtube_match:
        query = youtube_match.group(1).strip()
        result = youtube_search(query)
        return {
            "handled": True,
            "action": "web_search" if result.get("success") else "search_failed",
            "target": query,
            "engine": "youtube",
            "response": result.get("response", "I couldn't perform that search."),
        }

    google_direct = re.match(
        r"^google\s+(.+)$",
        text,
    )

    if google_direct:
        query = google_direct.group(1).strip()
        result = google_search(query)
        return {
            "handled": True,
            "action": "web_search" if result.get("success") else "search_failed",
            "target": query,
            "engine": "google",
            "response": result.get("response", "I couldn't perform that search."),
        }

    youtube_direct = re.match(
        r"^youtube\s+(.+)$",
        text,
    )

    if youtube_direct:
        query = youtube_direct.group(1).strip()
        result = youtube_search(query)
        return {
            "handled": True,
            "action": "web_search" if result.get("success") else "search_failed",
            "target": query,
            "engine": "youtube",
            "response": result.get("response", "I couldn't perform that search."),
        }

    return None


# ============================================================
# FOLDER OPEN
# ============================================================

def handle_folder_open(command):

    text = normalize(command)

    # --------------------------------------------------------
    # Standard folders
    # --------------------------------------------------------

    standard_pattern = re.match(
        r"^open\s+"
        r"(downloads|documents|desktop|pictures|music|videos)$",
        text,
    )

    if standard_pattern:

        folder = standard_pattern.group(1)

        return open_folder(folder)

    # --------------------------------------------------------
    # open folder college
    # --------------------------------------------------------

    folder_pattern = re.match(
        r"^open\s+folder\s+(.+)$",
        text,
    )

    if folder_pattern:

        folder = folder_pattern.group(1).strip()

        if folder:

            return open_folder(folder)

    # --------------------------------------------------------
    # open the college folder
    # --------------------------------------------------------

    the_folder_pattern = re.match(
        r"^open\s+the\s+(.+)\s+folder$",
        text,
    )

    if the_folder_pattern:

        folder = the_folder_pattern.group(1).strip()

        if folder:

            return open_folder(folder)

    # --------------------------------------------------------
    # open college folder
    # --------------------------------------------------------

    ending_folder_pattern = re.match(
        r"^open\s+(.+)\s+folder$",
        text,
    )

    if ending_folder_pattern:

        folder = ending_folder_pattern.group(1).strip()

        if folder:

            return open_folder(folder)

    return None


# ============================================================
# FOLDER CREATE
# ============================================================

def handle_folder_create(command):

    text = normalize(command)

    patterns = [
        r"^create\s+folder\s+(.+)$",
        r"^create\s+a\s+folder\s+(.+)$",
        r"^make\s+folder\s+(.+)$",
        r"^make\s+a\s+folder\s+(.+)$",
    ]

    for pattern in patterns:

        match = re.match(
            pattern,
            text,
        )

        if not match:
            continue

        folder_name = match.group(1).strip()

        # Supports:
        # called Aria Notes
        # named Aria Notes

        folder_name = re.sub(
            r"^(?:called|named)\s+",
            "",
            folder_name,
        ).strip()

        if not folder_name:

            return {
                "handled": True,
                "success": False,
                "response": (
                    "Tell me the name of the folder."
                ),
            }

        return create_folder(
            folder_name
        )

    return None


# ============================================================
# FOLDER DELETE
# ============================================================

def handle_folder_delete(command):

    global pending_folder_deletion

    text = normalize(command)

    # --------------------------------------------------------
    # HANDLE CONFIRMATION
    # --------------------------------------------------------

    if pending_folder_deletion is not None:

        # ----------------------------------------------------
        # YES / CONFIRM
        # ----------------------------------------------------

        affirmative_phrases = {
            "yes",
            "yeah",
            "yep",
            "yup",
            "yes please",
            "do it",
            "confirm",
            "confirmed",
            "delete it",
            "delete that",
            "delete that folder",
            "go ahead",
            "sure",
            "haan",
            "han",
            "ha",
            "ye",
            "y e",
            "y",
        }

        # Exact common confirmations
        if text in affirmative_phrases:

            folder_name = (
                pending_folder_deletion
            )

            pending_folder_deletion = None

            return delete_folder(
                folder_name
            )

        # ----------------------------------------------------
        # NATURAL CONFIRMATION SENTENCES
        # ----------------------------------------------------

        affirmative_patterns = [
            r"^(?:yes|yeah|yep|yup)\s+(?:delete|remove)(?:\s+.+)?$",
            r"^(?:yes|yeah|yep|yup)\s+please\s+(?:delete|remove)(?:\s+.+)?$",
            r"^(?:yes|yeah|yep|yup)\s+you\s+can\s+(?:delete|remove)(?:\s+.+)?$",
            r"^(?:yes|yeah|yep|yup)\s+(?:go\s+ahead|do\s+it)$",
            r"^(?:please\s+)?(?:go\s+ahead|do\s+it)$",
            r"^(?:sure|confirm|confirmed)\s+(?:delete|remove)(?:\s+.+)?$",
            r"^(?:haan|han|ha)\s+(?:delete|remove)(?:\s+.+)?$",
        ]

        confirmed = False

        for pattern in affirmative_patterns:

            if re.match(
                pattern,
                text,
            ):

                confirmed = True
                break

        if confirmed:

            folder_name = (
                pending_folder_deletion
            )

            pending_folder_deletion = None

            return delete_folder(
                folder_name
            )

        # ----------------------------------------------------
        # NO / CANCEL
        # ----------------------------------------------------

        negative_phrases = {
            "no",
            "nope",
            "nah",
            "cancel",
            "cancel it",
            "cancel that",
            "cancel deletion",
            "don't",
            "dont",
            "do not",
            "don't delete",
            "dont delete",
            "don't delete it",
            "dont delete it",
            "don't delete that",
            "dont delete that",
            "don't delete that folder",
            "dont delete that folder",
            "no thanks",
            "no don't",
            "no dont",
            "nahi",
            "nahin",
        }

        if text in negative_phrases:

            folder_name = (
                pending_folder_deletion
            )

            pending_folder_deletion = None

            return {
                "handled": True,
                "success": False,
                "action": "delete_cancelled",
                "target": folder_name,
                "response": (
                    f"Okay. I won't delete "
                    f"the folder {folder_name}."
                ),
            }

        # ----------------------------------------------------
        # NATURAL CANCELLATION SENTENCES
        # ----------------------------------------------------

        negative_patterns = [
            r"^(?:no|nope|nah)\s+(?:delete|remove)(?:\s+.+)?$",
            r"^(?:no|nope|nah)\s+(?:don't|dont|do\s+not)\s+(?:delete|remove)(?:\s+.+)?$",
            r"^(?:please\s+)?cancel(?:\s+it|\s+that|\s+deletion)?$",
            r"^(?:nahi|nahin)\s+(?:delete|remove)(?:\s+.+)?$",
        ]

        cancelled = False

        for pattern in negative_patterns:

            if re.match(
                pattern,
                text,
            ):

                cancelled = True
                break

        if cancelled:

            folder_name = (
                pending_folder_deletion
            )

            pending_folder_deletion = None

            return {
                "handled": True,
                "success": False,
                "action": "delete_cancelled",
                "target": folder_name,
                "response": (
                    f"Okay. I won't delete "
                    f"the folder {folder_name}."
                ),
            }

        # ----------------------------------------------------
        # UNKNOWN RESPONSE
        # ----------------------------------------------------

        return {
            "handled": True,
            "success": False,
            "action": (
                "delete_confirmation_required"
            ),
            "response": (
                "Please say yes to delete it "
                "or no to cancel."
            ),
        }

    # --------------------------------------------------------
    # NEW DELETE COMMAND
    # --------------------------------------------------------

    patterns = [

        # delete folder Aria Notes
        r"^delete\s+folder\s+(.+)$",

        # delete the folder Aria Notes
        r"^delete\s+the\s+folder\s+(.+)$",

        # delete folder named Aria Notes
        # delete folder called Aria Notes
        r"^delete\s+folder\s+"
        r"(?:named|called)\s+(.+)$",

        # delete the folder named Aria Notes
        # delete the folder called Aria Notes
        r"^delete\s+the\s+folder\s+"
        r"(?:named|called)\s+(.+)$",

        # remove folder Aria Notes
        r"^remove\s+folder\s+(.+)$",

        # remove the folder Aria Notes
        r"^remove\s+the\s+folder\s+(.+)$",

        # delete Aria Notes folder
        r"^delete\s+(.+)\s+folder$",

        # remove Aria Notes folder
        r"^remove\s+(.+)\s+folder$",
    ]

    for pattern in patterns:

        match = re.match(
            pattern,
            text,
        )

        if not match:
            continue

        folder_name = match.group(1).strip()

        # ----------------------------------------------------
        # Remove called/named if captured
        # ----------------------------------------------------

        folder_name = re.sub(
            r"^(?:called|named)\s+",
            "",
            folder_name,
        ).strip()

        if not folder_name:

            return {
                "handled": True,
                "success": False,
                "response": (
                    "Tell me the name of the "
                    "folder to delete."
                ),
            }

        # ----------------------------------------------------
        # Protected standard folders
        # ----------------------------------------------------

        protected_folders = {
            "downloads",
            "documents",
            "desktop",
            "pictures",
            "music",
            "videos",
        }

        if folder_name in protected_folders:

            return {
                "handled": True,
                "success": False,
                "action": "protected_folder",
                "target": folder_name,
                "response": (
                    f"I won't delete the "
                    f"{folder_name} system folder."
                ),
            }

        # ----------------------------------------------------
        # Find custom folder
        # ----------------------------------------------------

        matches = find_custom_folder(
            folder_name
        )

        if not matches:

            return {
                "handled": True,
                "success": False,
                "action": "folder_not_found",
                "target": folder_name,
                "response": (
                    f"I couldn't find a folder "
                    f"named {folder_name}."
                ),
            }

        # ----------------------------------------------------
        # Multiple matches
        # ----------------------------------------------------

        if len(matches) > 1:

            response = (
                f"I found multiple folders "
                f"named {folder_name}:"
            )

            for index, path in enumerate(
                matches,
                start=1,
            ):

                response += (
                    f"\n{index}. {path}"
                )

            return {
                "handled": True,
                "success": False,
                "action": (
                    "folder_selection_required"
                ),
                "target": folder_name,
                "matches": matches,
                "response": response,
            }

        # ----------------------------------------------------
        # Ask for confirmation
        # ----------------------------------------------------

        pending_folder_deletion = (
            matches[0]
        )

        return {
            "handled": True,
            "success": False,
            "action": (
                "delete_confirmation_required"
            ),
            "target": folder_name,
            "path": matches[0],
            "response": (
                f"I found the folder "
                f"{folder_name}. "
                "Are you sure you want me "
                "to delete it?"
            ),
        }

    return None


# ============================================================
# APPLICATION NAME MATCHING
# ============================================================

def normalized_app_name(name):

    name = normalize(name)

    name = re.sub(
        r"\s+\(launcher\)$",
        "",
        name,
        flags=re.IGNORECASE,
    )

    return name


def is_exact_app_match(
    query,
    result,
):

    query = normalized_app_name(
        query
    )

    result_name = normalized_app_name(
        result.get(
            "name",
            "",
        )
    )

    if not query or not result_name:
        return False

    # Direct exact match
    if query == result_name:
        return True

    # Alias match
    aliases = APP_ALIASES.get(
        query,
        [],
    )

    for alias in aliases:

        alias = normalized_app_name(
            alias
        )

        if result_name == alias:
            return True

    # VS Code
    vscode_queries = {
        "vscode",
        "vs code",
        "vs-code",
        "visual studio code",
    }

    if query in vscode_queries:

        return result_name in {
            "visual studio code",
            "code",
        }

    return False


# ============================================================
# FIND BEST APPLICATION
# ============================================================

def find_best_app_match(query):

    results = search_applications(
        query
    )

    if not results:
        return None, []

    exact_matches = []

    for result in results:

        if is_exact_app_match(
            query,
            result,
        ):

            exact_matches.append(
                result
            )

    if exact_matches:

        exact_matches.sort(
            key=lambda item: (
                0
                if item.get("type")
                == "start_menu"
                else 1,

                -item.get(
                    "score",
                    0,
                ),
            )
        )

        return (
            exact_matches[0],
            exact_matches,
        )

    good_matches = [
        result
        for result in results
        if result.get(
            "score",
            0,
        ) >= 0.75
    ]

    return (
        None,
        good_matches[:10],
    )


# ============================================================
# CHROME HELPERS
# ============================================================

def clean_chrome_target(text):

    text = normalize(text)

    replacements = [
        "google chrome",
        "chrome browser",
        "chrome",
    ]

    for replacement in replacements:

        text = text.replace(
            replacement,
            " ",
        )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def get_profile_display_names():

    profiles = get_chrome_profiles()

    names = []

    for profile in profiles:

        name = (
            profile.get("name")
            or profile.get("profile_name")
            or profile.get("alias")
        )

        if name and name not in names:

            names.append(name)

    return names


# ============================================================
# CHROME OPEN
# ============================================================

def handle_chrome_open(command):

    command_normalized = normalize(
        command
    )

    if "chrome" not in command_normalized:
        return None

    if not command_normalized.startswith(
        "open "
    ):
        return None

    target = re.sub(
        r"^open\s+",
        "",
        command_normalized,
    )

    target = clean_chrome_target(
        target
    )

    # --------------------------------------------------------
    # No profile specified
    # --------------------------------------------------------

    if not target:

        profiles = get_chrome_profiles()

        if not profiles:

            return {
                "handled": True,
                "action": (
                    "chrome_profile_not_found"
                ),
                "target": "",
                "response": (
                    "I couldn't find any "
                    "Chrome profiles."
                ),
            }

        if len(profiles) == 1:

            profile = profiles[0]

            open_managed_chrome_profile(
                profile
            )

            return {
                "handled": True,
                "action": "open_chrome",
                "target": profile.get(
                    "name"
                ),
                "response": (
                    f"Opening "
                    f"{profile.get('name')} "
                    "Chrome profile."
                ),
            }

        global pending_chrome_profiles

        pending_chrome_profiles = profiles

        options = "\n".join(
            f"{index + 1}. "
            f"{profile.get('name')}"
            for index, profile
            in enumerate(profiles)
        )

        return {
            "handled": True,
            "action": (
                "choose_chrome_profile"
            ),
            "response": (
                "Which Chrome profile "
                "should I open?\n"
                + options
            ),
        }

    # --------------------------------------------------------
    # Specific profile
    # --------------------------------------------------------

    profile = find_profile_by_alias(
        target
    )

    if profile:

        result = open_managed_chrome_profile(
            profile
        )

        if result:

            return {
                "handled": True,
                "action": "open_chrome",
                "target": profile.get(
                    "name"
                ),
                "response": (
                    f"Opening "
                    f"{profile.get('name')} "
                    "Chrome profile."
                ),
            }

    available = get_profile_display_names()

    return {
        "handled": True,
        "action": (
            "chrome_profile_not_found"
        ),
        "target": target,
        "response": (
            f"I couldn't find a Chrome "
            f"profile named {target}. "
            f"Available profiles are: "
            f"{', '.join(available)}."
        ),
    }


# ============================================================
# CHROME CLOSE
# ============================================================

def handle_chrome_close(command):

    command_normalized = normalize(
        command
    )

    if "chrome" not in command_normalized:
        return None

    if not command_normalized.startswith(
        "close "
    ):
        return None

    target = re.sub(
        r"^close\s+",
        "",
        command_normalized,
    )

    target = clean_chrome_target(
        target
    )

    # --------------------------------------------------------
    # Plain close chrome
    # --------------------------------------------------------

    if not target:

        profiles = get_chrome_profiles()

        if not profiles:

            return {
                "handled": True,
                "action": "chrome_not_found",
                "response": (
                    "I couldn't find any "
                    "Chrome profiles."
                ),
            }

        if len(profiles) == 1:

            profile = profiles[0]

            success = (
                close_managed_chrome_profile(
                    profile.get("name")
                )
            )

            if success:

                return {
                    "handled": True,
                    "action": "close_chrome",
                    "target": profile.get(
                        "name"
                    ),
                    "response": (
                        f"Closed "
                        f"{profile.get('name')} "
                        "Chrome."
                    ),
                }

            return {
                "handled": True,
                "action": (
                    "chrome_close_failed"
                ),
                "target": profile.get(
                    "name"
                ),
                "response": (
                    f"I couldn't close "
                    f"{profile.get('name')} "
                    "Chrome."
                ),
            }

        global pending_chrome_profiles

        pending_chrome_profiles = profiles

        options = "\n".join(
            f"{index + 1}. "
            f"{profile.get('name')}"
            for index, profile
            in enumerate(profiles)
        )

        return {
            "handled": True,
            "action": (
                "choose_chrome_profile_to_close"
            ),
            "response": (
                "Which Chrome profile "
                "should I close?\n"
                + options
            ),
        }

    # --------------------------------------------------------
    # Specific profile
    # --------------------------------------------------------

    profile = find_profile_by_alias(
        target
    )

    if not profile:

        available = get_profile_display_names()

        return {
            "handled": True,
            "action": (
                "chrome_profile_not_found"
            ),
            "target": target,
            "response": (
                f"I couldn't find a Chrome "
                f"profile named {target}. "
                f"Available profiles are: "
                f"{', '.join(available)}."
            ),
        }

    profile_name = profile.get(
        "name"
    )

    success = close_managed_chrome_profile(
        profile_name
    )

    if success:

        return {
            "handled": True,
            "action": "close_chrome",
            "target": profile_name,
            "response": (
                f"Closed {profile_name} Chrome."
            ),
        }

    return {
        "handled": True,
        "action": "chrome_close_failed",
        "target": profile_name,
        "response": (
            f"I couldn't close "
            f"{profile_name} Chrome."
        ),
    }


# ============================================================
# PENDING CHROME SELECTION
# ============================================================

def handle_pending_chrome_selection(
    command
):

    global pending_chrome_profiles

    if not pending_chrome_profiles:
        return None

    text = normalize(command)

    selected = None

    # Number selection
    number_match = re.fullmatch(
        r"\d+",
        text,
    )

    if number_match:

        index = int(
            number_match.group()
        ) - 1

        if (
            0 <= index
            < len(pending_chrome_profiles)
        ):

            selected = (
                pending_chrome_profiles[index]
            )

    # Name selection
    if selected is None:

        for profile in pending_chrome_profiles:

            name = normalize(
                profile.get(
                    "name",
                    "",
                )
            )

            if text == name:

                selected = profile
                break

    if selected is None:

        return {
            "handled": True,
            "action": (
                "invalid_chrome_selection"
            ),
            "response": (
                "I couldn't match that "
                "Chrome profile."
            ),
        }

    pending_chrome_profiles = []

    return {
        "handled": True,
        "action": "chrome_selection",
        "target": selected.get(
            "name"
        ),
        "profile": selected,
    }


# ============================================================
# PENDING APP SELECTION
# ============================================================

def handle_pending_app_selection(
    command
):

    global pending_app_results

    if not pending_app_results:
        return None

    text = normalize(command)

    if not re.fullmatch(
        r"\d+",
        text,
    ):
        return None

    index = int(text) - 1

    if not (
        0 <= index
        < len(pending_app_results)
    ):

        return {
            "handled": True,
            "action": (
                "invalid_app_selection"
            ),
            "response": (
                "That application "
                "number is not valid."
            ),
        }

    selected = pending_app_results[
        index
    ]

    pending_app_results = []

    success = open_search_result(
        selected
    )

    if success:

        return {
            "handled": True,
            "action": "open",
            "target": selected.get(
                "name"
            ),
            "response": (
                f"Opening "
                f"{selected.get('name')}."
            ),
        }

    return {
        "handled": True,
        "action": "open_failed",
        "target": selected.get(
            "name"
        ),
        "response": (
            f"I found "
            f"{selected.get('name')} "
            "but couldn't open it."
        ),
    }


# ============================================================
# NORMAL APPLICATION OPEN
# ============================================================

def handle_application_open(command):

    text = normalize(command)

    if not text.startswith("open "):
        return None

    target = text[5:].strip()

    if not target:
        return None

    # Chrome handled separately
    if "chrome" in target:
        return None

    # --------------------------------------------------------
    # VS CODE DIRECT ROUTING
    # --------------------------------------------------------

    vscode_targets = {
        "vscode",
        "vs code",
        "vs-code",
        "visual studio code",
        "code",
    }

    if target in vscode_targets:

        results = search_applications(
            "vscode"
        )

        vscode_result = None

        for result in results:

            result_name = normalized_app_name(
                result.get(
                    "name",
                    "",
                )
            )

            result_type = result.get(
                "type"
            )

            if (
                result_type == "vscode"
                and result_name
                == "visual studio code"
            ):

                vscode_result = result
                break

        # Fallback
        if vscode_result is None:

            for result in results:

                result_name = normalized_app_name(
                    result.get(
                        "name",
                        "",
                    )
                )

                if result_name == "code":

                    vscode_result = result
                    break

        if vscode_result:

            success = open_search_result(
                vscode_result
            )

            if success:

                return {
                    "handled": True,
                    "action": "open",
                    "target": (
                        "Visual Studio Code"
                    ),
                    "response": (
                        "Opening Visual Studio Code."
                    ),
                }

            return {
                "handled": True,
                "action": "open_failed",
                "target": (
                    "Visual Studio Code"
                ),
                "response": (
                    "I found Visual Studio Code "
                    "but couldn't open it."
                ),
            }

        return {
            "handled": True,
            "action": "not_found",
            "target": (
                "Visual Studio Code"
            ),
            "response": (
                "I couldn't find Visual Studio "
                "Code on your computer."
            ),
        }

    # --------------------------------------------------------
    # Normal application
    # --------------------------------------------------------

    best, exact_matches = (
        find_best_app_match(target)
    )

    if best:

        success = open_search_result(
            best
        )

        if success:

            return {
                "handled": True,
                "action": "open",
                "target": best.get(
                    "name"
                ),
                "response": (
                    f"Opening "
                    f"{best.get('name')}."
                ),
            }

        return {
            "handled": True,
            "action": "open_failed",
            "target": best.get(
                "name"
            ),
            "response": (
                f"I found "
                f"{best.get('name')} "
                "but couldn't open it."
            ),
        }

    # --------------------------------------------------------
    # Multiple exact matches
    # --------------------------------------------------------

    if len(exact_matches) > 1:

        unique = []
        names = set()

        for result in exact_matches:

            name = result.get(
                "name",
                "",
            )

            name_key = name.lower()

            if name_key not in names:

                names.add(name_key)
                unique.append(result)

        if len(unique) == 1:

            success = open_search_result(
                unique[0]
            )

            if success:

                return {
                    "handled": True,
                    "action": "open",
                    "target": unique[0].get(
                        "name"
                    ),
                    "response": (
                        f"Opening "
                        f"{unique[0].get('name')}."
                    ),
                }

        global pending_app_results

        pending_app_results = unique

        options = "\n".join(
            f"{index + 1}. "
            f"{item.get('name')}"
            for index, item
            in enumerate(unique)
        )

        return {
            "handled": True,
            "action": "choose_app",
            "response": (
                f"I found multiple matches "
                f"for {target}:\n"
                f"{options}"
            ),
        }

    return {
        "handled": True,
        "action": "not_found",
        "target": target,
        "response": (
            f"I couldn't find {target} "
            "on your computer."
        ),
    }


# ============================================================
# NORMAL APPLICATION CLOSE
# ============================================================

def handle_application_close(command):

    text = normalize(command)

    if not text.startswith("close "):
        return None

    target = text[6:].strip()

    if not target:
        return None

    # Chrome handled separately
    if "chrome" in target:
        return None

    result = close_application(target)

    if result.get("success"):
        return {
            "handled": True,
            "success": True,
            "action": "close",
            "target": target,
            "response": result.get(
                "response",
                f"Closed {target}."
            ),
        }

    return {
        "handled": True,
        "success": False,
        "action": "close_failed",
        "target": target,
        "response": result.get(
            "response",
            f"I couldn't close {target}."
        ),
    }


# ============================================================
# MAIN INTENT DETECTOR
# ============================================================

def detect_intent(command):

    command = command.strip()

    if not command:

        return {
            "handled": False
        }

    # --------------------------------------------------------
    # FOLDER DELETE / CONFIRMATION
    #
    # This must be first because responses like:
    # "yes"
    # "yes delete that folder"
    # "haan"
    # "y e"
    # need to be handled while deletion is pending.
    # --------------------------------------------------------

    normalized_command = normalize(
        command
    )

    if (
        pending_folder_deletion is not None
        or re.match(
            r"^(delete|remove)\s+",
            normalized_command,
        )
    ):

        result = handle_folder_delete(
            command
        )

        if result:
            return result

    # --------------------------------------------------------
    # Pending Chrome selection
    # --------------------------------------------------------

    if pending_chrome_profiles:

        result = (
            handle_pending_chrome_selection(
                command
            )
        )

        if result:

            if (
                result.get("action")
                == "chrome_selection"
            ):

                profile = result.get(
                    "profile"
                )

                success = (
                    open_managed_chrome_profile(
                        profile
                    )
                )

                if success:

                    return {
                        "handled": True,
                        "action": "open_chrome",
                        "target": profile.get(
                            "name"
                        ),
                        "response": (
                            f"Opening "
                            f"{profile.get('name')} "
                            "Chrome profile."
                        ),
                    }

            return result

    # --------------------------------------------------------
    # Pending normal app selection
    # --------------------------------------------------------

    if pending_app_results:

        result = (
            handle_pending_app_selection(
                command
            )
        )

        if result:
            return result

    # --------------------------------------------------------
    # FOLDER OPEN
    #
    # Must happen before web search.
    # --------------------------------------------------------

    result = handle_folder_open(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # FOLDER CREATE
    # --------------------------------------------------------

    result = handle_folder_create(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # WEB SEARCH
    # --------------------------------------------------------

    result = handle_web_search(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # WEBSITE OPEN
    # --------------------------------------------------------

    result = handle_website_open(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # CHROME OPEN
    # --------------------------------------------------------

    result = handle_chrome_open(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # CHROME CLOSE
    # --------------------------------------------------------

    result = handle_chrome_close(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # NORMAL APP OPEN
    # --------------------------------------------------------

    result = handle_application_open(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # NORMAL APP CLOSE
    # --------------------------------------------------------

    result = handle_application_close(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # NOTHING HANDLED
    # --------------------------------------------------------

    return {
        "handled": False
    }


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print(" ARIA INTENT SYSTEM TEST")
    print("==========================================")
    print()

    test_commands = [

        # ----------------------------------------------------
        # Websites
        # ----------------------------------------------------

        "open youtube",
        "open gmail",
        "open github",
        "open instagram",
        "open google",

        # ----------------------------------------------------
        # Web search
        # ----------------------------------------------------

        "search google for Python projects",
        "search youtube for Aria AI assistant",
        "google Python projects",
        "youtube Aria AI assistant",

        # ----------------------------------------------------
        # Standard folders
        # ----------------------------------------------------

        "open downloads",
        "open documents",
        "open desktop",
        "open pictures",
        "open music",
        "open videos",

        # ----------------------------------------------------
        # Custom folders
        # ----------------------------------------------------

        "open folder college",
        "open college folder",
        "open the college folder",

        # ----------------------------------------------------
        # Folder creation
        # ----------------------------------------------------

        "create folder Aria Notes",
        "create a folder Test Files",
        "create a folder called College Work",
        "create a folder named Projects",
        "make folder Aria Work",
        "make a folder Test Folder",
        "make a folder called College",

        # ----------------------------------------------------
        # Folder deletion
        # ----------------------------------------------------

        "delete folder Aria Notes",
        "delete the folder named Aria Notes",
        "delete the folder called Aria Notes",
        "remove folder Aria Notes",
        "remove the folder named Aria Notes",
        "delete Aria Notes folder",

        # ----------------------------------------------------
        # VS Code
        # ----------------------------------------------------

        "open vscode",
        "open vs code",
        "open vs-code",
        "open visual studio code",
        "open code",
        "close vscode",

        # ----------------------------------------------------
        # Applications
        # ----------------------------------------------------

        "open notepad",
        "close notepad",
        "open calculator",
        "close calculator",
        "close edge",
        "close terminal",
        "close powershell",

        # ----------------------------------------------------
        # Chrome
        # ----------------------------------------------------

        "open college chrome",
        "open Satyam chrome",
        "close college chrome",
        "close Satyam chrome",
    ]

    for command in test_commands:

        print()
        print(f"> {command}")

        result = detect_intent(
            command
        )

        print(result)