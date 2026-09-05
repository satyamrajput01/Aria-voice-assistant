def detect_emotion(text: str) -> tuple[str, float]:
    """
    Temporary emotion detector for development.

    This analyzes the transcribed text.
    Later this file will be replaced/upgraded with
    actual voice/audio emotion detection.
    """

    text = text.lower().strip()

    if not text:
        return "neutral", 0.0

    sad_words = [
        "sad",
        "depressed",
        "lonely",
        "alone",
        "cry",
        "crying",
        "upset",
        "hurt",
        "broken",
        "terrible",
        "awful",
        "bad day",
        "low",
        "unhappy",
        "दुखी",
        "उदास",
        "अकेला",
        "अकेली",
        "रोना",
        "परेशान",
        "बुरा",
    ]

    angry_words = [
        "angry",
        "mad",
        "furious",
        "annoyed",
        "irritated",
        "hate",
        "गुस्सा",
        "नाराज़",
        "परेशान",
    ]

    tired_words = [
        "tired",
        "exhausted",
        "sleepy",
        "sleep",
        "exhausted",
        "थका",
        "थकी",
        "थक गया",
        "थक गई",
        "नींद",
    ]

    happy_words = [
        "happy",
        "great",
        "amazing",
        "awesome",
        "wonderful",
        "good",
        "love it",
        "खुश",
        "बहुत अच्छा",
        "मज़ा",
    ]

    excited_words = [
        "excited",
        "wow",
        "omg",
        "can't wait",
        "amazing news",
        "यार कमाल",
        "बहुत excited",
    ]

    scores = {
        "sad": 0,
        "angry": 0,
        "tired": 0,
        "happy": 0,
        "excited": 0,
    }

    for word in sad_words:
        if word in text:
            scores["sad"] += 1

    for word in angry_words:
        if word in text:
            scores["angry"] += 1

    for word in tired_words:
        if word in text:
            scores["tired"] += 1

    for word in happy_words:
        if word in text:
            scores["happy"] += 1

    for word in excited_words:
        if word in text:
            scores["excited"] += 1

    emotion = max(scores, key=scores.get)
    score = scores[emotion]

    if score == 0:
        return "neutral", 0.50

    confidence = min(0.60 + (score * 0.10), 0.95)

    return emotion, confidence


if __name__ == "__main__":

    tests = [
        "I am feeling really sad today",
        "I am so tired",
        "I am really angry",
        "I am very happy today",
        "I am so excited",
        "Tell me about Python"
    ]

    for text in tests:
        emotion, confidence = detect_emotion(text)
        print(f"{text}")
        print(f"Emotion: {emotion} | Confidence: {confidence:.2f}")
        print()