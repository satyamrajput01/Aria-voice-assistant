import re

from commands.computer_search import (
    search_computer,
    open_search_result,
)

from core.system_control import (
    close_application,
)


# ---------------------------------------------------------
# Pending computer selection
# ---------------------------------------------------------

pending_results = []
pending_type = None


# ---------------------------------------------------------
# Basic text cleaning
# ---------------------------------------------------------

def clean_input(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()

    text = re.sub(
        r"^\s*(?:aria|arya)[\s,:-]*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()


# ---------------------------------------------------------
# Remove command words
# ---------------------------------------------------------

def clean_target(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    patterns = [
        r"^open\s+",
        r"^launch\s+",
        r"^start\s+",
        r"^run\s+",
        r"^go\s+to\s+",
        r"^show\s+",
    ]

    for pattern in patterns:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE,
        )

    return text.strip()


# ---------------------------------------------------------
# Check whether this is an open command
# ---------------------------------------------------------

def is_open_command(text: str) -> bool:

    patterns = [
        r"^open\s+",
        r"^launch\s+",
        r"^start\s+",
        r"^run\s+",
        r"^go\s+to\s+",
        r"^show\s+",
    ]

    for pattern in patterns:

        if re.match(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            return True

    return False


# ---------------------------------------------------------
# Extract number from natural language
# ---------------------------------------------------------

def extract_selection_number(
    text: str,
):
    """
    Understand selections such as:

    5
    number 5
    option 5
    the fifth one
    fifth
    fifth one
    """

    if not text:
        return None

    text = text.lower().strip()

    # -----------------------------------------------------
    # Direct numbers
    # -----------------------------------------------------

    match = re.fullmatch(
        r"(?:number|option|choice)?\s*(\d+)",
        text,
        flags=re.IGNORECASE,
    )

    if match:

        return int(
            match.group(1)
        )

    # -----------------------------------------------------
    # Ordinal words
    # -----------------------------------------------------

    ordinal_numbers = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "sixth": 6,
        "seventh": 7,
        "eighth": 8,
        "ninth": 9,
        "tenth": 10,
    }

    cleaned = re.sub(
        r"\b(the|one|option|choice|number)\b",
        " ",
        text,
    )

    cleaned = " ".join(
        cleaned.split()
    )

    if cleaned in ordinal_numbers:

        return ordinal_numbers[
            cleaned
        ]

    # -----------------------------------------------------
    # Natural phrases
    #
    # Example:
    #
    # "the fifth one please"
    # "I want the second one"
    # -----------------------------------------------------

    for word, number in ordinal_numbers.items():

        if re.search(
            rf"\b{word}\b",
            text,
        ):

            allowed_words = {
                "the",
                "one",
                "option",
                "choice",
                "number",
                "please",
                "i",
                "want",
                "open",
                "select",
                "pick",
                "choose",
                word,
            }

            words = set(
                re.findall(
                    r"[a-z]+",
                    text,
                )
            )

            if words.issubset(
                allowed_words
            ):

                return number

    return None


# ---------------------------------------------------------
# Remove conversational selection words
# ---------------------------------------------------------

def clean_selection_text(
    text: str,
) -> str:

    text = text.lower().strip()

    patterns = [
        r"^open\s+",
        r"^launch\s+",
        r"^start\s+",
        r"^run\s+",
        r"^show\s+",
        r"^go\s+to\s+",
        r"^i\s+want\s+",
        r"^i\s+choose\s+",
        r"^i\s+pick\s+",
        r"^choose\s+",
        r"^pick\s+",
        r"^select\s+",
        r"^please\s+",
    ]

    changed = True

    while changed:

        changed = False

        for pattern in patterns:

            new_text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE,
            )

            if new_text != text:

                text = new_text.strip()
                changed = True

    text = re.sub(
        r"^the\s+",
        "",
        text,
    )

    return text.strip()


# ---------------------------------------------------------
# Format multiple results
# ---------------------------------------------------------

def build_selection_response(
    results,
):

    lines = [
        "I found several matches."
    ]

    for index, result in enumerate(
        results,
        start=1,
    ):

        lines.append(
            f"{index}. {result['name']}"
        )

    lines.append(
        "Which one should I open?"
    )

    return "\n".join(lines)


# ---------------------------------------------------------
# Match user's selection
# ---------------------------------------------------------

def select_pending_result(
    user_input: str,
):

    global pending_results
    global pending_type

    if not pending_results:
        return None

    text = clean_input(
        user_input
    )

    if not text:
        return None

    # -----------------------------------------------------
    # 1. Natural number selection
    # -----------------------------------------------------

    number = extract_selection_number(
        text
    )

    if number is not None:

        if 1 <= number <= len(
            pending_results
        ):

            result = pending_results[
                number - 1
            ]

            pending_results = []
            pending_type = None

            return result

    # -----------------------------------------------------
    # 2. Clean conversational words
    # -----------------------------------------------------

    selection_text = (
        clean_selection_text(text)
    )

    # -----------------------------------------------------
    # 3. Exact name match
    # -----------------------------------------------------

    exact_matches = []

    for result in pending_results:

        name = result[
            "name"
        ].lower().strip()

        if selection_text == name:

            exact_matches.append(
                result
            )

    if len(exact_matches) == 1:

        result = exact_matches[0]

        pending_results = []
        pending_type = None

        return result

    # -----------------------------------------------------
    # 4. Partial name match
    # -----------------------------------------------------

    partial_matches = []

    for result in pending_results:

        name = result[
            "name"
        ].lower().strip()

        if (
            selection_text in name
            or name in selection_text
        ):

            partial_matches.append(
                result
            )

    if len(partial_matches) == 1:

        result = partial_matches[0]

        pending_results = []
        pending_type = None

        return result

    return None


# ---------------------------------------------------------
# Handle pending selection
# ---------------------------------------------------------

def handle_pending_selection(
    user_input: str,
):

    if not pending_results:
        return None

    result = select_pending_result(
        user_input
    )

    if not result:

        return {
            "handled": True,
            "action": "selection_required",
            "target": None,
            "response": build_selection_response(
                pending_results
            ),
        }

    success = open_search_result(
        result
    )

    if success:

        return {
            "handled": True,
            "action": "open_selected",
            "target": result["name"],
            "response": (
                f"Opening "
                f"{result['name']}."
            ),
        }

    return {
        "handled": True,
        "action": "open_failed",
        "target": result["name"],
        "response": (
            f"I found "
            f"{result['name']} "
            f"but I couldn't open it."
        ),
    }


# ---------------------------------------------------------
# Dynamic application closing
# ---------------------------------------------------------

def handle_dynamic_close(
    user_input: str,
):

    text = clean_input(
        user_input
    )

    if not text:
        return None

    patterns = [
        r"^close\s+(.+)$",
        r"^exit\s+(.+)$",
        r"^quit\s+(.+)$",
        r"^stop\s+(.+)$",
    ]

    target = None

    for pattern in patterns:

        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:

            target = match.group(
                1
            ).strip()

            break

    if not target:
        return None

    success = close_application(
        target
    )

    if success:

        return {
            "handled": True,
            "action": "close_application",
            "target": target,
            "response": (
                f"Closing {target}."
            ),
        }

    return {
        "handled": True,
        "action": "close_failed",
        "target": target,
        "response": (
            f"I couldn't find "
            f"a running application "
            f"matching {target}."
        ),
    }


# ---------------------------------------------------------
# Dynamic computer search
# ---------------------------------------------------------

def handle_dynamic_open(
    user_input: str,
):

    global pending_results
    global pending_type

    text = clean_input(
        user_input
    )

    if not text:
        return None

    if not is_open_command(
        text
    ):
        return None

    target = clean_target(
        text
    )

    if not target:
        return None

    # -----------------------------------------------------
    # Search applications first
    # -----------------------------------------------------

    results = search_computer(
        target,
        item_type="application",
    )

    # -----------------------------------------------------
    # If no application found,
    # search folders
    # -----------------------------------------------------

    if not results:

        results = search_computer(
            target,
            item_type="folder",
        )

        if results:
            pending_type = "folder"

    else:

        pending_type = "application"

    # -----------------------------------------------------
    # Nothing found
    # -----------------------------------------------------

    if not results:

        pending_results = []
        pending_type = None

        return {
            "handled": True,
            "action": "not_found",
            "target": target,
            "response": (
                f"I couldn't find "
                f"{target} on your computer."
            ),
        }

    # -----------------------------------------------------
    # One result
    # -----------------------------------------------------

    if len(results) == 1:

        result = results[0]

        pending_results = []
        pending_type = None

        success = open_search_result(
            result
        )

        if success:

            if result["type"] in {
                "application",
                "windows_application",
            }:

                action = (
                    "open_application"
                )

            else:

                action = "open_folder"

            return {
                "handled": True,
                "action": action,
                "target": result["name"],
                "response": (
                    f"Opening "
                    f"{result['name']}."
                ),
            }

        return {
            "handled": True,
            "action": "open_failed",
            "target": result["name"],
            "response": (
                f"I found "
                f"{result['name']} "
                f"but I couldn't open it."
            ),
        }

    # -----------------------------------------------------
    # Multiple results
    # -----------------------------------------------------

    pending_results = results

    return {
        "handled": True,
        "action": "selection_required",
        "target": target,
        "response": build_selection_response(
            results
        ),
    }


# ---------------------------------------------------------
# Main intent detector
# ---------------------------------------------------------

def detect_intent(
    user_input: str,
):

    if not user_input:

        return {
            "handled": False,
            "action": None,
            "target": None,
            "response": None,
        }

    # -----------------------------------------------------
    # Pending selection gets priority
    # -----------------------------------------------------

    if pending_results:

        result = handle_pending_selection(
            user_input
        )

        if result:
            return result

    # -----------------------------------------------------
    # CLOSE commands
    # -----------------------------------------------------

    result = handle_dynamic_close(
        user_input
    )

    if result:
        return result

    # -----------------------------------------------------
    # OPEN commands
    # -----------------------------------------------------

    result = handle_dynamic_open(
        user_input
    )

    if result:
        return result

    # -----------------------------------------------------
    # Nothing handled
    # -----------------------------------------------------

    return {
        "handled": False,
        "action": None,
        "target": None,
        "response": None,
    }


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "Aria Dynamic Intent Test"
    )

    print(
        "------------------------"
    )

    test_commands = [
        "Arya open Google Chrome",
        "Arya open Microsoft",
        "the fifth one",
        "Arya close Chrome",
        "Arya open code",
        "the first one",
    ]

    for command in test_commands:

        print()
        print(
            "Input:",
            command,
        )

        result = detect_intent(
            command
        )

        print(
            "Result:",
            result
        )