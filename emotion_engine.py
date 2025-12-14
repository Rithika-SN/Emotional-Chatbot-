# emotion_engine.py
# Utilities for emotion detection, tone analysis, day summary generation

import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Simple keyword-based emotion lexicons (expandable)
EMOTION_KEYWORDS = {
    "stress": ["stress", "stressed", "overwhelmed", "pressure", "panic", "anxious", "anxiety"],
    "sad": ["sad", "down", "depressed", "upset", "unhappy", "cry"],
    "happy": ["happy", "good", "great", "awesome", "glad", "joyful"],
    "motivated": ["motivated", "determined", "driven", "focused"],
    "bored": ["bored", "boredom", "uninterested", "dull"],
}

TONE_KEYWORDS = {
    "angry": ["angry", "mad", "furious", "irritated"],
    "polite": ["please", "thank you", "thanks"],
    "confused": ["don't understand", "confused", "lost", "not sure"],
    "neutral": []
}

analyzer = SentimentIntensityAnalyzer()

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def detect_emotions(text: str) -> dict:
    """
    Returns dict with:
      - dominant_emotion: one of keys in EMOTION_KEYWORDS or 'neutral'
      - emotion_scores: counts for each emotion
      - sentiment: compound VADER score
    """
    t = clean_text(text)
    emotion_counts = {k: 0 for k in EMOTION_KEYWORDS.keys()}
    for emo, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                emotion_counts[emo] += t.count(kw)

    # Fallback: use VADER polarity to pick positive/negative
    vs = analyzer.polarity_scores(t)
    compound = vs['compound']

    # determine dominant
    dominant = max(emotion_counts, key=lambda k: emotion_counts[k])
    if emotion_counts[dominant] == 0:
        # decide based on sentiment
        if compound <= -0.35:
            dominant = "stress"  # negative -> stress/sad
        elif compound >= 0.3:
            dominant = "happy"
        else:
            dominant = "neutral"

    return {
        "dominant_emotion": dominant,
        "emotion_counts": emotion_counts,
        "sentiment_compound": compound
    }

def detect_tone(text: str) -> str:
    t = clean_text(text)
    for tone, keywords in TONE_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                return tone
    # fallback using punctuation and sentiment
    if t.endswith("!"):
        return "angry" if analyzer.polarity_scores(t)['compound'] < 0 else "excited"
    return "neutral"

def generate_day_summary(messages: list) -> str:
    """
    messages: list of dicts: {"text": "...", "emotion": "...", "tone": "..."}
    Returns short summary string.
    """
    if not messages:
        return "No messages today."

    counts = {}
    
    for m in messages:
        e = m.get("emotion", "neutral")
        counts[e] = counts.get(e, 0) + 1

    # find top emotion(s)
    top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    primary_emotion, primary_count = top[0]

    avg_sent = 0
    for m in messages:
        avg_sent += m.get("sentiment_compound", 0)
    avg_sent = avg_sent / max(1, len(messages))

    summary = f"Today's dominant mood: {primary_emotion}. "
    summary += f"You sent {len(messages)} messages. Average sentiment score: {avg_sent:.2f}. "

    if primary_emotion in ("stress", "sad"):
        summary += "It seems like today was a bit tough — remember to take breaks, try a short breathing exercise, and consider writing down 3 small wins."
    elif primary_emotion == "happy":
        summary += "Looks like a positive day — great job! Keep the momentum going."
    elif primary_emotion == "motivated":
        summary += "You're in a motivated state — schedule your hardest task in your most productive hour."
    else:
        summary += "A mixed or neutral day. Try short study sprints (25 mins) with mini-breaks."

    return summary
