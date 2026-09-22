import os
import shutil


FOLDER_ALIASES = {
    "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
    "documents": os.path.join(os.path.expanduser("~"), "Documents"),
    "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
    "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
    "music": os.path.join(os.path.expanduser("~"), "Music"),
    "videos": os.path.join(os.path.expanduser("~"), "Videos"),
}


PROTECTED_FOLDERS = {
    "desktop",
    "documents",
    "downloads",
    "pictures",
    "music",
    "videos",
}


SEARCH_LOCATIONS = [
    FOLDER_ALIASES["desktop"],
    FOLDER_ALIASES["documents"],
    FOLDER_ALIASES["downloads"],
]


def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def get_folder_path(folder_name: str):
    folder_name = normalize(folder_name)

    if folder_name in FOLDER_ALIASES:
        return FOLDER_ALIASES[folder_name]

    return None


def find_custom_folder(folder_name: str):
    """
    Searches for an exact folder-name match inside:
    Desktop
    Documents
    Downloads

    Only immediate folders are searched.
    """

    folder_name = folder_name.strip()

    if not folder_name:
        return []


    matches = []

    for base_path in SEARCH_LOCATIONS:

        if not os.path.exists(base_path):
            continue

        try:
            for item in os.listdir(base_path):

                full_path = os.path.join(base_path, item)

                if not os.path.isdir(full_path):
                    continue

                if item.lower() == folder_name.lower():
                    if full_path not in matches:
                        matches.append(full_path)

        except PermissionError:
            print(f"Permission denied while searching: {base_path}")

        except Exception as error:
            print(f"Folder search error: {error}")


    return matches


def open_folder(folder_name: str):

    original_name = folder_name.strip()
    normalized_name = normalize(folder_name)

    # Standard Windows folders
    standard_path = get_folder_path(normalized_name)

    if standard_path:

        if not os.path.exists(standard_path):
            return {
                "handled": True,
                "success": False,
                "response": f"The {original_name} folder does not exist."
            }

        try:
            os.startfile(standard_path)

            return {
                "handled": True,
                "success": True,
                "action": "open_folder",
                "target": original_name,
                "path": standard_path,
                "response": f"Opening {original_name}."
            }

        except Exception as error:
            print(f"Folder open error: {error}")

            return {
                "handled": True,
                "success": False,
                "response": f"I couldn't open the {original_name} folder."
            }


    # Custom folder search
    matches = find_custom_folder(original_name)

    if not matches:

        return {
            "handled": True,
            "success": False,
            "response": f"I couldn't find a folder named {original_name}."
        }


    if len(matches) > 1:

        paths = "\n".join(matches)

        return {
            "handled": True,
            "success": False,
            "multiple_matches": True,
            "paths": matches,
            "response": (
                f"I found multiple folders named {original_name}:\n"
                f"{paths}"
            )
        }


    folder_path = matches[0]

    try:
        os.startfile(folder_path)

        return {
            "handled": True,
            "success": True,
            "action": "open_folder",
            "target": original_name,
            "path": folder_path,
            "response": f"Opening {original_name}."
        }

    except Exception as error:

        print(f"Folder open error: {error}")

        return {
            "handled": True,
            "success": False,
            "response": f"I couldn't open the {original_name} folder."
        }


def create_folder(folder_name: str):

    folder_name = folder_name.strip()

    if not folder_name:

        return {
            "handled": True,
            "success": False,
            "response": "Tell me the name of the folder."
        }


    desktop = FOLDER_ALIASES["desktop"]
    folder_path = os.path.join(desktop, folder_name)

    try:

        os.makedirs(folder_path, exist_ok=True)

        return {
            "handled": True,
            "success": True,
            "action": "create_folder",
            "target": folder_name,
            "path": folder_path,
            "response": (
                f"Created a folder named {folder_name} on your desktop."
            )
        }

    except Exception as error:

        print(f"Folder creation error: {error}")

        return {
            "handled": True,
            "success": False,
            "response": f"I couldn't create the folder {folder_name}."
        }


def delete_folder(folder_path: str):

    if not folder_path:
        return {
            "handled": True,
            "success": False,
            "response": "I couldn't determine which folder to delete."
        }


    folder_path = os.path.abspath(folder_path)

    if not os.path.exists(folder_path):

        return {
            "handled": True,
            "success": False,
            "response": "That folder no longer exists."
        }


    if not os.path.isdir(folder_path):

        return {
            "handled": True,
            "success": False,
            "response": "That path is not a folder."
        }


    # Safety protection for important Windows folders
    folder_name = os.path.basename(folder_path).lower()

    protected_paths = {
        os.path.abspath(path).lower()
        for path in FOLDER_ALIASES.values()
    }

    if folder_path.lower() in protected_paths:

        return {
            "handled": True,
            "success": False,
            "response": "I won't delete one of your standard Windows folders."
        }


    if folder_name in PROTECTED_FOLDERS:

        return {
            "handled": True,
            "success": False,
            "response": "I won't delete a protected system folder."
        }


    try:

        # Permanent deletion
        shutil.rmtree(folder_path)

        return {
            "handled": True,
            "success": True,
            "action": "delete_folder",
            "target": folder_name,
            "path": folder_path,
            "response": f"Deleted the folder {folder_name}."
        }

    except PermissionError:

        return {
            "handled": True,
            "success": False,
            "response": (
                f"I couldn't delete {folder_name} because "
                "Windows denied permission."
            )
        }

    except Exception as error:

        print(f"Folder deletion error: {error}")

        return {
            "handled": True,
            "success": False,
            "response": f"I couldn't delete the folder {folder_name}."
        }


def open_file(path: str):

    path = os.path.expandvars(
        os.path.expanduser(path.strip())
    )

    if not os.path.exists(path):

        return {
            "handled": True,
            "success": False,
            "response": "I couldn't find that file."
        }


    if not os.path.isfile(path):

        return {
            "handled": True,
            "success": False,
            "response": "That path is not a file."
        }


    try:

        os.startfile(path)

        return {
            "handled": True,
            "success": True,
            "action": "open_file",
            "target": path,
            "response": "Opening the file."
        }

    except Exception as error:

        print(f"File open error: {error}")

        return {
            "handled": True,
            "success": False,
            "response": "I couldn't open that file."
        }