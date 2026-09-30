import re
import webbrowser
from urllib.parse import quote_plus


# ============================================================
# COMMON WEBSITE ALIASES
# ============================================================

WEBSITE_ALIASES = {
    # Search
    "google": "https://www.google.com/",
    "google search": "https://www.google.com/",

    # Video / media
    "youtube": "https://www.youtube.com/",
    "youtube music": "https://music.youtube.com/",
    "netflix": "https://www.netflix.com/",
    "spotify": "https://open.spotify.com/",
    "prime video": "https://www.primevideo.com/",
    "amazon prime": "https://www.primevideo.com/",

    # Social
    "instagram": "https://www.instagram.com/",
    "facebook": "https://www.facebook.com/",
    "twitter": "https://x.com/",
    "x": "https://x.com/",
    "linkedin": "https://www.linkedin.com/",
    "reddit": "https://www.reddit.com/",
    "discord": "https://discord.com/",
    "telegram": "https://web.telegram.org/",

    # Google services
    "gmail": "https://mail.google.com/",
    "google mail": "https://mail.google.com/",
    "google drive": "https://drive.google.com/",
    "drive": "https://drive.google.com/",
    "google docs": "https://docs.google.com/",
    "docs": "https://docs.google.com/",
    "google sheets": "https://sheets.google.com/",
    "sheets": "https://sheets.google.com/",
    "google slides": "https://slides.google.com/",
    "slides": "https://slides.google.com/",
    "google meet": "https://meet.google.com/",
    "meet": "https://meet.google.com/",
    "google maps": "https://maps.google.com/",
    "maps": "https://maps.google.com/",

    # Development
    "github": "https://github.com/",
    "git hub": "https://github.com/",
    "gitlab": "https://gitlab.com/",
    "bitbucket": "https://bitbucket.org/",
    "stackoverflow": "https://stackoverflow.com/",
    "stack overflow": "https://stackoverflow.com/",
    "npm": "https://www.npmjs.com/",
    "pypi": "https://pypi.org/",
    "python": "https://www.python.org/",
    "mozilla": "https://developer.mozilla.org/",
    "mdn": "https://developer.mozilla.org/",

    # AI
    "chatgpt": "https://chatgpt.com/",
    "chat gpt": "https://chatgpt.com/",
    "gemini": "https://gemini.google.com/",
    "claude": "https://claude.ai/",
    "perplexity": "https://www.perplexity.ai/",
    "hugging face": "https://huggingface.co/",
    "huggingface": "https://huggingface.co/",

    # Shopping
    "amazon": "https://www.amazon.in/",
    "flipkart": "https://www.flipkart.com/",
    "myntra": "https://www.myntra.com/",
    "meesho": "https://www.meesho.com/",
    "ajio": "https://www.ajio.com/",

    # Education
    "coursera": "https://www.coursera.org/",
    "udemy": "https://www.udemy.com/",
    "w3schools": "https://www.w3schools.com/",
    "geeksforgeeks": "https://www.geeksforgeeks.org/",
    "geeks for geeks": "https://www.geeksforgeeks.org/",

    # News / information
    "wikipedia": "https://www.wikipedia.org/",
    "medium": "https://medium.com/",
    "quora": "https://www.quora.com/",

    # Productivity
    "notion": "https://www.notion.so/",
    "canva": "https://www.canva.com/",
    "figma": "https://www.figma.com/",
    "trello": "https://trello.com/",
    "zoom": "https://zoom.us/",
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize spoken website names.
    """

    if not text:
        return ""

    text = str(text).lower().strip()

    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================
# REMOVE OPEN WEBSITE COMMAND WORDS
# ============================================================

def clean_website_query(query):
    """
    Convert things like:

        "open youtube"
        "open the youtube website"
        "go to github"
        "visit google"

    into:

        "youtube"
        "github"
        "google"
    """

    query = normalize_text(query)

    prefixes = [
        r"^open\s+",
        r"^go\s+to\s+",
        r"^visit\s+",
        r"^launch\s+",
        r"^browse\s+",
        r"^navigate\s+to\s+",
    ]

    for pattern in prefixes:
        query = re.sub(pattern, "", query)

    suffixes = [
        r"\s+website$",
        r"\s+site$",
        r"\s+web\s*site$",
    ]

    for pattern in suffixes:
        query = re.sub(pattern, "", query)

    return query.strip()


# ============================================================
# URL DETECTION
# ============================================================

def is_url(text):
    """
    Check whether text already looks like a URL.
    """

    if not text:
        return False

    text = text.strip()

    # Explicit protocol
    if re.match(r"^https?://", text, re.IGNORECASE):
        return True

    # www.example.com
    if re.match(
        r"^www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}",
        text,
        re.IGNORECASE,
    ):
        return True

    # example.com / example.co.in / example.org
    if re.match(
        r"^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?",
        text,
        re.IGNORECASE,
    ):
        return True

    return False


# ============================================================
# URL NORMALIZATION
# ============================================================

def normalize_url(url):
    """
    Convert a domain into a browser-ready URL.

    Example:
        github.com
        ->
        https://github.com/
    """

    url = url.strip()

    if re.match(r"^https?://", url, re.IGNORECASE):
        return url

    if url.lower().startswith("www."):
        return "https://" + url

    return "https://" + url


# ============================================================
# RESOLVE WEBSITE
# ============================================================

def resolve_website(query):
    """
    Resolve a website name or URL.

    Priority:

    1. Known alias
    2. Direct URL/domain
    """

    cleaned = clean_website_query(query)

    if not cleaned:
        return None

    # --------------------------------------------------------
    # Known website alias
    # --------------------------------------------------------

    if cleaned in WEBSITE_ALIASES:
        return WEBSITE_ALIASES[cleaned]

    # --------------------------------------------------------
    # Direct URL/domain
    # --------------------------------------------------------

    if is_url(cleaned):
        return normalize_url(cleaned)

    return None


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(query):
    """
    Open a website in the user's default browser.

    Supports:

        open youtube
        open github
        open instagram
        open example.com
        open https://example.com
    """

    cleaned = clean_website_query(query)

    if not cleaned:
        return {
            "success": False,
            "response": "I couldn't understand which website to open.",
        }

    url = resolve_website(cleaned)

    if not url:
        return {
            "success": False,
            "name": cleaned,
            "response": (
                f"I couldn't identify {cleaned} as a website. "
                "You can give me a website name or domain."
            ),
        }

    try:
        opened = webbrowser.open(url, new=2)

        if opened:
            return {
                "success": True,
                "name": cleaned,
                "url": url,
                "response": f"Opening {cleaned}.",
            }

        return {
            "success": False,
            "name": cleaned,
            "url": url,
            "response": f"I couldn't open {cleaned}.",
        }

    except Exception as error:
        return {
            "success": False,
            "name": cleaned,
            "url": url,
            "response": f"Website opening error: {error}",
        }


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(query):
    """
    Search Google for a query.
    """

    if not query:
        return {
            "success": False,
            "response": "I need something to search for.",
        }

    query = str(query).strip()

    url = (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )

    try:
        opened = webbrowser.open(url, new=2)

        if opened:
            return {
                "success": True,
                "query": query,
                "url": url,
                "response": f"Searching Google for {query}.",
            }

        return {
            "success": False,
            "response": "I couldn't open Google search.",
        }

    except Exception as error:
        return {
            "success": False,
            "response": f"Google search error: {error}",
        }


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(query):
    """
    Search YouTube for a query.
    """

    if not query:
        return {
            "success": False,
            "response": "I need something to search for on YouTube.",
        }

    query = str(query).strip()

    url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(query)
    )

    try:
        opened = webbrowser.open(url, new=2)

        if opened:
            return {
                "success": True,
                "query": query,
                "url": url,
                "response": f"Searching YouTube for {query}.",
            }

        return {
            "success": False,
            "response": "I couldn't open YouTube search.",
        }

    except Exception as error:
        return {
            "success": False,
            "response": f"YouTube search error: {error}",
        }


# ============================================================
# GENERAL WEBSITE SEARCH
# ============================================================

def search_website(site, query):
    """
    Search a supported website.

    Currently supported:
        Google
        YouTube

    Other websites can still be opened normally.
    """

    site = normalize_text(site)

    if site in {
        "google",
        "google search",
    }:
        return google_search(query)

    if site in {
        "youtube",
        "youtube search",
    }:
        return youtube_search(query)

    return {
        "success": False,
        "response": (
            f"I can open {site}, but I don't have "
            f"search support for it yet."
        ),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n=== WEBSITE RESOLVER TEST ===")

    test_sites = [
        "youtube",
        "github",
        "instagram",
        "chatgpt",
        "google drive",
        "example.com",
        "https://developer.mozilla.org/",
    ]

    for site in test_sites:
        print(
            f"{site} -> "
            f"{resolve_website(site)}"
        )

    print("\n=== DONE ===")