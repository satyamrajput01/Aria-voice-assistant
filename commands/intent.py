import re

from commands.computer_search import (
    search_applications,
    open_search_result,
)

from commands.chrome_control import (
    get_chrome_profiles,
    find_profile_by_alias,
    open_managed_chrome_profile,
    close_managed_chrome_profile,
)


# ============================================================
# STATE
# ============================================================

pending_app_results = []
pending_chrome_profiles = []


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
    """
    Normalize user command text.
    """

    if not text:
        return ""

    text = text.lower().strip()

    text = text.replace("-", " ")
    text = text.replace("_", " ")

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# APP NAME MATCHING
# ============================================================

def normalized_app_name(name):
    """
    Normalize an application name for comparison.
    """

    name = normalize(name)

    name = re.sub(
        r"\s*\(launcher\)$",
        "",
        name,
        flags=re.IGNORECASE,
    )

    return name


def is_exact_app_match(query, result):
    """
    Check whether a search result is an exact or alias match.

    This prevents commands such as:

        open vscode
        open vs code
        open visual studio code

    from being confused with:

        CodeBlocks
        CodeBlocks Launcher
        other applications containing 'code'
    """

    query = normalized_app_name(query)

    result_name = normalized_app_name(
        result.get("name", "")
    )

    if not query or not result_name:
        return False

    # --------------------------------------------------------
    # Direct exact match
    # --------------------------------------------------------

    if query == result_name:
        return True

    # --------------------------------------------------------
    # Alias match
    # --------------------------------------------------------

    aliases = APP_ALIASES.get(
        query,
        []
    )

    for alias in aliases:

        alias = normalized_app_name(
            alias
        )

        if result_name == alias:
            return True

    # --------------------------------------------------------
    # VS CODE SPECIAL HANDLING
    # --------------------------------------------------------

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
    """
    Find one strong application match.

    Exact and alias matches always win over
    fuzzy matches.
    """

    results = search_applications(
        query
    )

    if not results:
        return None, []

    exact_matches = []

    for result in results:

        if is_exact_app_match(
            query,
            result
        ):

            exact_matches.append(
                result
            )

    # --------------------------------------------------------
    # Exact match found
    # --------------------------------------------------------

    if exact_matches:

        # Prefer Start Menu application.
        exact_matches.sort(
            key=lambda item: (
                0
                if item.get("type")
                == "start_menu"
                else 1,

                -item.get(
                    "score",
                    0
                ),
            )
        )

        return (
            exact_matches[0],
            exact_matches
        )

    # --------------------------------------------------------
    # No exact match
    # --------------------------------------------------------

    good_matches = [
        result
        for result in results
        if result.get(
            "score",
            0
        ) >= 0.75
    ]

    return (
        None,
        good_matches[:10]
    )


# ============================================================
# CHROME HELPERS
# ============================================================

def clean_chrome_target(text):
    """
    Remove Chrome-related words from a command.
    """

    text = normalize(text)

    replacements = [
        "google chrome",
        "chrome browser",
        "chrome",
    ]

    for replacement in replacements:

        text = text.replace(
            replacement,
            " "
        )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def get_profile_display_names():
    """
    Get available Chrome profile names.
    """

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
    """
    Handle commands such as:

        open college chrome
        open Satyam chrome
        open Uma chrome
        open Hansini chrome
    """

    command_normalized = normalize(
        command
    )

    if "chrome" not in command_normalized:
        return None

    if not command_normalized.startswith(
        "open "
    ):
        return None

    target = command_normalized

    target = re.sub(
        r"^open\s+",
        "",
        target,
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
                "action": "chrome_profile_not_found",
                "target": "",
                "response": (
                    "I couldn't find any Chrome profiles."
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

        return {
            "handled": True,
            "action": "choose_chrome_profile",
            "response": (
                "Which Chrome profile should I open?\n"
                + "\n".join(
                    f"{index + 1}. "
                    f"{profile.get('name')}"
                    for index, profile
                    in enumerate(profiles)
                )
            ),
        }

    # --------------------------------------------------------
    # Specific Chrome profile
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
        "action": "chrome_profile_not_found",
        "target": target,
        "response": (
            f"I couldn't find a Chrome profile "
            f"named {target}. "
            f"Available profiles are: "
            f"{', '.join(available)}."
        ),
    }


# ============================================================
# CHROME CLOSE
# ============================================================

def handle_chrome_close(command):
    """
    Handle:

        close college chrome
        close Satyam chrome
        close Uma chrome
        close Hansini chrome
        close chrome
    """

    command_normalized = normalize(
        command
    )

    if "chrome" not in command_normalized:
        return None

    if not command_normalized.startswith(
        "close "
    ):
        return None

    target = command_normalized

    target = re.sub(
        r"^close\s+",
        "",
        target,
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
                    "I couldn't find any Chrome profiles."
                ),
            }

        if len(profiles) == 1:

            profile = profiles[0]

            success = close_managed_chrome_profile(
                profile.get("name")
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
                "action": "chrome_close_failed",
                "target": profile.get(
                    "name"
                ),
                "response": (
                    f"I couldn't close "
                    f"{profile.get('name')} "
                    "Chrome."
                ),
            }

        return {
            "handled": True,
            "action": "choose_chrome_profile_to_close",
            "response": (
                "Which Chrome profile should I close?\n"
                + "\n".join(
                    f"{index + 1}. "
                    f"{profile.get('name')}"
                    for index, profile
                    in enumerate(profiles)
                )
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
            "action": "chrome_profile_not_found",
            "target": target,
            "response": (
                f"I couldn't find a Chrome profile "
                f"named {target}. "
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

def handle_pending_chrome_selection(command):
    """
    Handle selection after Aria asks which Chrome
    profile should be opened.
    """

    global pending_chrome_profiles

    if not pending_chrome_profiles:
        return None

    text = normalize(
        command
    )

    selected = None

    # --------------------------------------------------------
    # Number selection
    # --------------------------------------------------------

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
                pending_chrome_profiles[
                    index
                ]
            )

    # --------------------------------------------------------
    # Name selection
    # --------------------------------------------------------

    if selected is None:

        for profile in pending_chrome_profiles:

            name = normalize(
                profile.get(
                    "name",
                    ""
                )
            )

            if text == name:

                selected = profile
                break

    if selected is None:

        return {
            "handled": True,
            "action": "invalid_chrome_selection",
            "response": (
                "I couldn't match that Chrome profile."
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

def handle_pending_app_selection(command):
    """
    Handle numeric application selection.
    """

    global pending_app_results

    if not pending_app_results:
        return None

    text = normalize(
        command
    )

    if not re.fullmatch(
        r"\d+",
        text
    ):
        return None

    index = int(text) - 1

    if not (
        0 <= index
        < len(pending_app_results)
    ):

        return {
            "handled": True,
            "action": "invalid_app_selection",
            "response": (
                "That application number is not valid."
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
    """
    Handle normal application opening.

    Examples:

        open vscode
        open vs code
        open vs-code
        open visual studio code
        open notepad
        open calculator
    """

    text = normalize(
        command
    )

    if not text.startswith(
        "open "
    ):
        return None

    target = text[5:].strip()

    if not target:
        return None

    # Chrome handled separately.
    if "chrome" in target:
        return None

    # --------------------------------------------------------
    # VS CODE DIRECT ROUTING
    # --------------------------------------------------------
    # This is intentionally before the general search.
    # It guarantees that:
    #
    # open vscode
    # open vs code
    # open vs-code
    # open visual studio code
    #
    # all open Visual Studio Code directly.
    # --------------------------------------------------------

    vscode_targets = {
        "vscode",
        "vs code",
        "vs-code",
        "visual studio code",
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
                    ""
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

        # Fallback to executable result.
        if vscode_result is None:

            for result in results:

                result_name = normalized_app_name(
                    result.get(
                        "name",
                        ""
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
                    "target": "Visual Studio Code",
                    "response": (
                        "Opening Visual Studio Code."
                    ),
                }

            return {
                "handled": True,
                "action": "open_failed",
                "target": "Visual Studio Code",
                "response": (
                    "I found Visual Studio Code "
                    "but couldn't open it."
                ),
            }

        return {
            "handled": True,
            "action": "not_found",
            "target": "Visual Studio Code",
            "response": (
                "I couldn't find Visual Studio Code "
                "on your computer."
            ),
        }

    # --------------------------------------------------------
    # NORMAL APPLICATION SEARCH
    # --------------------------------------------------------

    best, exact_matches = find_best_app_match(
        target
    )

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

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
    # Genuine ambiguity
    # --------------------------------------------------------

    if len(exact_matches) > 1:

        unique = []
        names = set()

        for result in exact_matches:

            name = result.get(
                "name",
                ""
            )

            name_key = name.lower()

            if name_key not in names:

                names.add(name_key)
                unique.append(
                    result
                )

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
                f"I found multiple matches for "
                f"{target}:\n{options}"
            ),
        }

    # --------------------------------------------------------
    # Nothing found
    # --------------------------------------------------------

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
    """
    Handle normal application closing.

    Chrome is excluded because Chrome profiles
    require special handling.
    """

    text = normalize(
        command
    )

    if not text.startswith(
        "close "
    ):
        return None

    target = text[6:].strip()

    if not target:
        return None

    if "chrome" in target:
        return None

    return {
        "handled": True,
        "action": "close",
        "target": target,
        "response": (
            f"Closing {target}."
        ),
    }


# ============================================================
# MAIN INTENT DETECTOR
# ============================================================

def detect_intent(command):
    """
    Main intent router.
    """

    global pending_app_results
    global pending_chrome_profiles

    command = command.strip()

    if not command:

        return {
            "handled": False
        }

    # --------------------------------------------------------
    # Pending Chrome selection
    # --------------------------------------------------------

    if pending_chrome_profiles:

        result = handle_pending_chrome_selection(
            command
        )

        if result:

            if (
                result.get(
                    "action"
                )
                == "chrome_selection"
            ):

                profile = result.get(
                    "profile"
                )

                success = open_managed_chrome_profile(
                    profile
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

        result = handle_pending_app_selection(
            command
        )

        if result:
            return result

    # --------------------------------------------------------
    # Chrome OPEN
    # --------------------------------------------------------

    result = handle_chrome_open(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # Chrome CLOSE
    # --------------------------------------------------------

    result = handle_chrome_close(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # Normal APP OPEN
    # --------------------------------------------------------

    result = handle_application_open(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # Normal APP CLOSE
    # --------------------------------------------------------

    result = handle_application_close(
        command
    )

    if result:
        return result

    # --------------------------------------------------------
    # Nothing handled
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
        "open vscode",
        "open vs code",
        "open vs-code",
        "open visual studio code",
        "open code",
        "close vscode",
        "open notepad",
        "close notepad",
        "open calculator",
        "close calculator",
        "open college chrome",
        "open Satyam chrome",
        "close college chrome",
        "close Satyam chrome",
    ]

    for command in test_commands:

        print()
        print(
            f"> {command}"
        )

        result = detect_intent(
            command
        )

        print(
            result
        )