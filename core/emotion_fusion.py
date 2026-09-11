from collections import deque
import re


# Keep a short emotional history so Aria can understand continuity.
EMOTION_HISTORY = deque(maxlen=6)


# ============================================================
# TEXT SIGNALS
# ============================================================

STRONG_EMOTION_PHRASES = {
    "sad": [
        "i am very sad",
        "i'm very sad",
        "i am really sad",
        "i'm really sad",
        "i feel sad",
        "i feel really sad",
        "i feel lonely",
        "i am lonely",
        "i'm lonely",
        "i feel depressed",
        "i am heartbroken",
        "i'm heartbroken",
        "i feel terrible",
        "i feel awful",
    ],

    "angry": [
        "i am very angry",
        "i'm very angry",
        "i am really angry",
        "i'm really angry",
        "i am furious",
        "i'm furious",
        "i am pissed",
        "i'm pissed",
        "i hate this",
        "this is making me angry",
        "i am extremely angry",
    ],

    "happy": [
        "i am very happy",
        "i'm very happy",
        "i am really happy",
        "i'm really happy",
        "i feel happy",
        "i feel really happy",
        "i am so happy",
        "i'm so happy",
        "i feel great",
        "i feel amazing",
        "i am doing great",
        "i'm doing great",
    ],

    "excited": [
        "i am excited",
        "i'm excited",
        "i am really excited",
        "i'm really excited",
        "i am so excited",
        "i'm so excited",
        "i feel excited",
        "i'm extremely excited",
        "i cannot believe it",
        "i can't believe it",
        "this is amazing",
        "this is awesome",
        "so excited",
    ],

    "tired": [
        "i am tired",
        "i'm tired",
        "i am really tired",
        "i'm really tired",
        "i am very tired",
        "i'm very tired",
        "i feel tired",
        "i am exhausted",
        "i'm exhausted",
        "i feel exhausted",
        "i am drained",
        "i'm drained",
        "i feel drained",
        "i have no energy",
        "i don't have energy",
        "i dont have energy",
        "no energy",
        "i need to rest",
        "i just want to rest",
        "i want to sleep",
        "i need some rest",
        "i don't feel like doing anything",
        "i dont feel like doing anything",
    ],
}


# Words that strongly indicate a particular state.
STATE_KEYWORDS = {
    "tired": [
        "tired",
        "exhausted",
        "exhaustion",
        "drained",
        "sleepy",
        "sleep",
        "rest",
        "resting",
        "energy",
        "exhausted",
        "fatigued",
        "fatigue",
        "lazy",
    ],

    "excited": [
        "excited",
        "exciting",
        "amazingly",
        "amazing",
        "awesome",
        "wow",
        "can't believe",
        "cannot believe",
        "incredible",
        "incredibly",
        "thrilled",
        "thrilling",
        "yay",
    ],

    "happy": [
        "happy",
        "great",
        "good",
        "awesome",
        "amazing",
        "wonderful",
        "fantastic",
        "love",
        "loving",
        "glad",
        "joy",
        "fun",
    ],

    "sad": [
        "sad",
        "lonely",
        "alone",
        "cry",
        "crying",
        "upset",
        "hurt",
        "heartbroken",
        "terrible",
        "awful",
        "hopeless",
    ],

    "angry": [
        "angry",
        "furious",
        "irritated",
        "irritating",
        "annoyed",
        "annoying",
        "mad",
        "pissed",
        "hate",
        "frustrated",
        "frustrating",
    ],
}


# Hindi / Hinglish signals.
HINDI_STATE_KEYWORDS = {
    "tired": [
        "thak",
        "thaka",
        "thaki",
        "thak gaya",
        "thak gayi",
        "thak chuka",
        "thak chuki",
        "bahut thak",
        "aaram",
        "so jaana",
        "sona hai",
        "neend",
        "energy nahi",
        "taqat nahi",
    ],

    "excited": [
        "excited",
        "bahut excited",
        "maza aa raha",
        "kya baat hai",
        "amazing",
        "awesome",
        "zabardast",
        "mast",
    ],

    "happy": [
        "khush",
        "bahut khush",
        "acha lag raha",
        "achha lag raha",
        "maza aa raha",
        "pyaar",
        "badiya",
        "mast",
    ],

    "sad": [
        "dukhi",
        "udaas",
        "akela",
        "akelapan",
        "rona",
        "ro raha",
        "ro rahi",
        "bura lag raha",
        "pareshan",
        "dard",
    ],

    "angry": [
        "gussa",
        "bahut gussa",
        "gusse",
        "chidh",
        "chidh raha",
        "chidh rahi",
        "pareshan",
        "irritated",
        "irritate",
        "frustrated",
    ],
}


# Neutral phrases should prevent weak voice predictions
# from changing an otherwise normal conversation.
NEUTRAL_PATTERNS = [
    "what can you do",
    "what do you do",
    "who are you",
    "what is your name",
    "tell me about yourself",
    "can you help me",
    "can you tell me",
    "how are you",
    "what is this",
    "what does this mean",
    "open",
    "launch",
    "search",
    "play",
    "set a reminder",
    "tell me a joke",
    "give me a joke",
    "good morning",
    "good evening",
    "good night",
    "hello",
    "hi",
    "hey",
]


RECOVERY_PATTERNS = [
    "i am okay",
    "i'm okay",
    "i am fine",
    "i'm fine",
    "i feel better",
    "i am feeling better",
    "i'm feeling better",
    "everything is okay",
    "everything is fine",
    "all good",
    "nothing is wrong",
]


# ============================================================
# HELPERS
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize English / Hinglish text for easier matching.
    """
    if not text:
        return ""

    text = text.lower().strip()

    # Normalize apostrophes.
    text = text.replace("’", "'")
    text = text.replace("‘", "'")

    # Remove extra punctuation while keeping apostrophes.
    text = re.sub(r"[^a-z0-9\u0900-\u097F\s']", " ", text)

    # Collapse spaces.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_any(text: str, phrases: list[str]) -> bool:
    """
    Check whether any phrase exists in the text.
    """
    return any(phrase in text for phrase in phrases)


def count_keywords(text: str, keywords: list[str]) -> int:
    """
    Count how many emotional/state keywords appear.
    """
    count = 0

    for keyword in keywords:
        if keyword in text:
            count += 1

    return count


def detect_text_state(text: str):
    """
    Detect emotional/state information from the actual words.

    Returns:
        (emotion, confidence, source)
    """

    text = normalize_text(text)

    if not text:
        return "neutral", 0.60, "neutral-text"

    # --------------------------------------------------------
    # 1. Strong explicit phrases
    # --------------------------------------------------------

    for emotion, phrases in STRONG_EMOTION_PHRASES.items():
        if contains_any(text, phrases):
            return emotion, 1.0, "strong-text"

    # --------------------------------------------------------
    # 2. Recovery phrases
    # --------------------------------------------------------

    if contains_any(text, RECOVERY_PATTERNS):
        return "neutral", 0.85, "recovery-text"

    # --------------------------------------------------------
    # 3. Neutral conversational requests
    # --------------------------------------------------------

    if contains_any(text, NEUTRAL_PATTERNS):
        return "neutral", 0.90, "neutral-text"

    # --------------------------------------------------------
    # 4. Hindi / Hinglish
    # --------------------------------------------------------

    hindi_scores = {}

    for emotion, keywords in HINDI_STATE_KEYWORDS.items():
        score = count_keywords(text, keywords)

        if score > 0:
            hindi_scores[emotion] = score

    if hindi_scores:
        best_emotion = max(hindi_scores, key=hindi_scores.get)
        best_score = hindi_scores[best_emotion]

        confidence = min(0.55 + (best_score * 0.12), 0.90)

        return best_emotion, confidence, "text-state"

    # --------------------------------------------------------
    # 5. English state detection
    # --------------------------------------------------------

    scores = {}

    for emotion, keywords in STATE_KEYWORDS.items():
        score = count_keywords(text, keywords)

        if score > 0:
            scores[emotion] = score

    if scores:
        best_emotion = max(scores, key=scores.get)
        best_score = scores[best_emotion]

        # Multiple matching keywords = stronger evidence.
        confidence = min(0.55 + (best_score * 0.12), 0.90)

        return best_emotion, confidence, "text-state"

    return "neutral", 0.60, "neutral-text"


# ============================================================
# MAIN FUSION FUNCTION
# ============================================================

def detect_fused_emotion(
    text: str,
    voice_emotion: str = "neutral",
    voice_confidence: float = 0.0
):
    """
    Combine:

        1. Text emotion/state
        2. Voice emotion
        3. Recent emotional context

    Supported final states:

        neutral
        happy
        sad
        angry
        tired
        excited
    """

    text = normalize_text(text)

    voice_emotion = (voice_emotion or "neutral").lower().strip()

    try:
        voice_confidence = float(voice_confidence)
    except Exception:
        voice_confidence = 0.0

    # --------------------------------------------------------
    # TEXT SIGNAL
    # --------------------------------------------------------

    text_emotion, text_confidence, text_source = detect_text_state(text)

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    previous_emotions = list(EMOTION_HISTORY)

    same_previous_emotion = None

    if previous_emotions:
        last_emotion = previous_emotions[-1]

        if last_emotion in [
            "sad",
            "happy",
            "angry",
            "tired",
            "excited",
        ]:
            same_previous_emotion = last_emotion

    # --------------------------------------------------------
    # STRONG TEXT ALWAYS WINS
    # --------------------------------------------------------

    if text_source == "strong-text":
        final_emotion = text_emotion
        final_confidence = text_confidence

        EMOTION_HISTORY.append(final_emotion)

        return final_emotion, final_confidence, text_source

    # --------------------------------------------------------
    # EXPLICIT TIRED STATE
    #
    # FairHindiSER has no tired class.
    # Therefore tired words must override a voice prediction
    # such as sad when the user explicitly says they are tired.
    # --------------------------------------------------------

    if text_emotion == "tired" and text_source == "text-state":
        final_emotion = "tired"

        # Stronger if several tired keywords are present.
        if count_keywords(text, STATE_KEYWORDS["tired"]) >= 2:
            final_confidence = 0.90
        else:
            final_confidence = 0.82

        EMOTION_HISTORY.append(final_emotion)

        return final_emotion, final_confidence, "text-state"

    # --------------------------------------------------------
    # EXPLICIT EXCITED STATE
    #
    # Excited is also not one of FairHindiSER's classes.
    # Happy voice + excited words should become excited.
    # --------------------------------------------------------

    if text_emotion == "excited":
        final_emotion = "excited"

        if count_keywords(text, STATE_KEYWORDS["excited"]) >= 2:
            final_confidence = 0.90
        else:
            final_confidence = 0.82

        EMOTION_HISTORY.append(final_emotion)

        return final_emotion, final_confidence, "text-state"

    # --------------------------------------------------------
    # NEUTRAL TEXT
    #
    # Weak voice predictions shouldn't hijack normal questions.
    # --------------------------------------------------------

    if text_source == "neutral-text":
        # Very strong voice emotion can still matter.
        if voice_confidence >= 0.85 and voice_emotion in [
            "sad",
            "happy",
            "angry",
        ]:
            final_emotion = voice_emotion
            final_confidence = voice_confidence
            source = "voice"

        else:
            final_emotion = "neutral"
            final_confidence = 0.60
            source = "neutral-text"

        EMOTION_HISTORY.append(final_emotion)

        return final_emotion, final_confidence, source

    # --------------------------------------------------------
    # TEXT + VOICE AGREE
    # --------------------------------------------------------

    if (
        text_emotion in ["sad", "happy", "angry"]
        and voice_emotion == text_emotion
    ):
        final_emotion = text_emotion

        final_confidence = min(
            max(text_confidence, voice_confidence),
            0.98
        )

        EMOTION_HISTORY.append(final_emotion)

        return final_emotion, final_confidence, "text+voice"

    # --------------------------------------------------------
    # STRONG VOICE
    # --------------------------------------------------------

    if voice_confidence >= 0.85 and voice_emotion in [
        "sad",
        "happy",
        "angry",
    ]:
        final_emotion = voice_emotion
        final_confidence = voice_confidence

        EMOTION_HISTORY.append(final_emotion)

        return final_emotion, final_confidence, "voice"

    # --------------------------------------------------------
    # MEDIUM VOICE + MATCHING CONTEXT
    # --------------------------------------------------------

    if (
        voice_confidence >= 0.70
        and voice_emotion in ["sad", "happy", "angry"]
        and same_previous_emotion == voice_emotion
    ):
        final_emotion = voice_emotion
        final_confidence = min(
            voice_confidence + 0.05,
            0.90
        )

        EMOTION_HISTORY.append(final_emotion)

        return final_emotion, final_confidence, "voice+context"

    # --------------------------------------------------------
    # MEDIUM VOICE WITHOUT CONTEXT
    # --------------------------------------------------------

    if (
        voice_confidence >= 0.70
        and voice_emotion in ["sad", "happy", "angry"]
    ):
        final_emotion = voice_emotion
        final_confidence = min(
            voice_confidence * 0.85,
            0.85
        )

        EMOTION_HISTORY.append(final_emotion)

        return final_emotion, final_confidence, "voice"

    # --------------------------------------------------------
    # MODERATE TEXT SIGNAL
    # --------------------------------------------------------

    if (
        text_emotion in ["sad", "happy", "angry"]
        and text_confidence >= 0.65
    ):
        final_emotion = text_emotion
        final_confidence = text_confidence

        EMOTION_HISTORY.append(final_emotion)

        return final_emotion, final_confidence, "text"

    # --------------------------------------------------------
    # WEAK VOICE + CONTEXT
    # --------------------------------------------------------

    if (
        voice_confidence >= 0.45
        and voice_emotion in ["sad", "happy", "angry"]
        and same_previous_emotion == voice_emotion
    ):
        final_emotion = voice_emotion
        final_confidence = 0.65

        EMOTION_HISTORY.append(final_emotion)

        return final_emotion, final_confidence, "voice+context"

    # --------------------------------------------------------
    # OTHERWISE NEUTRAL
    # --------------------------------------------------------

    final_emotion = "neutral"
    final_confidence = 0.60

    EMOTION_HISTORY.append(final_emotion)

    return final_emotion, final_confidence, "neutral"