# app.py
import streamlit as st
from emotion_engine import detect_emotions, detect_tone, generate_day_summary
from data_store import add_message_record, get_today_messages, get_all_messages
import json
from pathlib import Path
import random
from datetime import datetime

RESP_FILE = Path("responses.json")
if RESP_FILE.exists():
    responses = json.loads(RESP_FILE.read_text(encoding="utf-8"))
else:
    responses = {}

st.set_page_config(page_title="EmoBuddy - Student Emotional Companion", layout="centered")

def main():
    st.title("🌱 EmoBuddy — Emotional Companion for Students")
    st.markdown("I help you track mood, suggest study habits, and offer short supportive responses. (Not a medical tool.)")

    # Simple user selection (single-user demo)
    user_id = st.text_input("Your user id (any name)", value="student_1")

    st.sidebar.header("Quick actions")
    if st.sidebar.button("Show today's summary"):
        msgs = get_today_messages(user_id)
        # transform into messages for summary
        msgs_parsed = [{"text": m["text"], "emotion": m["emotion"], "tone": m["tone"], "sentiment_compound": m["sentiment"]} for m in msgs]
        st.sidebar.write(generate_day_summary(msgs_parsed))

    st.sidebar.write("Saved messages: " + str(len(get_all_messages(user_id))))

    st.markdown("---")
    col1, col2 = st.columns([3,1])
    with col1:
        st.header("Chat with EmoBuddy")
        chat_input = st.text_area("Type your message here...", height=120)
        if st.button("Send"):
            if not chat_input.strip():
                st.info("Type something and press Send.")
            else:
                process_message(user_id, chat_input)
    with col2:
        st.header("Mood Dashboard")
        all_msgs = get_all_messages(user_id)
        if all_msgs:
            # simple counts
            counts = {}
            for m in all_msgs:
                counts[m["emotion"]] = counts.get(m["emotion"], 0) + 1
            st.write("Mood counts (all time):")
            st.table([{ "emotion": k, "count": v } for k, v in counts.items()])

            # last 5 messages
            st.write("Recent messages:")
            for r in all_msgs[-5:]:
                st.write(f"- [{r['timestamp']}] {r['text']} ({r['emotion']}, {r['tone']})")
        else:
            st.write("No messages yet. Say hi!")

    st.markdown("---")
    st.caption("Tip: use natural language. EmoBuddy stores messages locally in user_data.json")

def process_message(user_id, text):
    # detect
    result = detect_emotions(text)
    tone = detect_tone(text)
    dominant = result["dominant_emotion"]
    sentiment = result["sentiment_compound"]

    # Save record
    record = add_message_record(user_id, text, dominant, tone, sentiment)

    # Choose reply template
    reply = compose_reply(dominant, tone, text, sentiment)
    st.success(reply)

    # show quick suggestions
    st.write("**Suggestions:**")
    suggests = responses.get("suggestions", {}).get(dominant, [])
    if suggests:
        for s in random.sample(suggests, min(2, len(suggests))):
            st.write("- " + s)
    else:
        for s in random.sample(responses.get("fallbacks", ["Take a deep breath."]), 1):
            st.write("- " + s)

    # show day summary preview
    msgs = get_all_messages(user_id)
    msgs_parsed = [{"text": m["text"], "emotion": m["emotion"], "tone": m["tone"], "sentiment_compound": m["sentiment"]} for m in msgs if date_is_today(m["timestamp"])]
    if msgs_parsed:
        st.info("Today's summary preview:")
        st.write(generate_day_summary(msgs_parsed))

def compose_reply(emotion, tone, text, sentiment):
    # friendly response mapping (simple)
    greetings = responses.get("greetings", ["Thanks for sharing."])
    base = random.choice(greetings)

    # emotion-tailored sentence
    if emotion == "stress":
        emo_line = "I'm sorry you're feeling stressed — that's tough."
    elif emotion == "sad":
        emo_line = "I'm sorry to hear you're feeling down."
    elif emotion == "happy":
        emo_line = "That's wonderful to hear!"
    elif emotion == "motivated":
        emo_line = "Awesome — you're in a motivated mood!"
    elif emotion == "bored":
        emo_line = "I hear you — boredom can make focus hard."
    else:
        emo_line = "Thanks for sharing how you're feeling."

    # tone tweak
    if tone == "angry":
        tone_line = "I can sense some strong emotion — breathing for 1 minute could help."
    elif tone == "confused":
        tone_line = "If you're confused, breaking the problem into tiny steps often helps."
    else:
        tone_line = ""

    return f"{base} {emo_line} {tone_line}"

def date_is_today(timestamp_iso):
    # crude check for same date (UTC)
    try:
        dt = datetime.fromisoformat(timestamp_iso.replace("Z", "+00:00"))
        today = datetime.utcnow().date()
        return dt.date() == today
    except Exception:
        return False

if __name__ == "__main__":
    main()
