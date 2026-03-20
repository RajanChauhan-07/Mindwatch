import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

POSITIVE_WORDS = [
    "happy", "great", "good", "love", "amazing", "wonderful", "excited",
    "awesome", "fantastic", "joy", "glad", "fun", "nice", "thanks", "thank",
    "beautiful", "brilliant", "excellent", "yay", "haha", "lol",
]
POSITIVE_EMOJIS = ["😊", "❤️", "😍", "😂", "🥰", "😄", "😁", "🎉", "✨", "💕"]

NEGATIVE_WORDS = [
    "sad", "bad", "hate", "angry", "depressed", "anxious", "worried",
    "terrible", "awful", "horrible", "tired", "exhausted", "alone",
    "lonely", "scared", "stress", "cry", "miss", "sorry",
]
NEGATIVE_EMOJIS = ["😢", "😭", "😔", "😞", "😟", "😩", "😫", "💔", "😰", "😥"]

STOP_WORDS = {
    "the", "a", "an", "is", "it", "in", "on", "at", "to", "for", "of",
    "and", "or", "but", "i", "you", "we", "he", "she", "they", "me",
    "my", "your", "our", "this", "that", "with", "are", "was", "be",
    "have", "has", "had", "do", "did", "will", "can", "could", "would",
    "should", "not", "no", "so", "up", "if", "as", "by", "from", "what",
    "how", "when", "where", "who", "which", "there", "here", "just",
    "ok", "okay", "yeah", "yes", "no", "oh", "ah", "hi", "hey", "hello",
    "omitted", "media", "image", "video", "sticker", "gif", "audio",
}

SYSTEM_MESSAGE_PATTERNS = [
    r"messages and calls are end-to-end encrypted",
    r"<media omitted>",
    r"this message was deleted",
    r"you deleted this message",
    r"missed voice call",
    r"missed video call",
    r"created group",
    r"added you",
    r"left",
    r"changed the subject",
    r"changed this group",
    r"changed the group",
    r"security code",
    r"your security code",
]

FORMATS = [
    # Format 1: [MM/DD/YY, H:MM:SS AM/PM] Name: message
    re.compile(r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?\s*[AP]M)\]\s*([^:]+):\s*(.+)$", re.IGNORECASE),
    # Format 2: DD/MM/YYYY, HH:MM - Name: message
    re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)$"),
    # Format 3: MM/DD/YYYY, HH:MM - Name: message
    re.compile(r"^(\d{1,2}/\d{1,2}/\d{4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)$"),
    # Format 4: M/D/YY, H:MM AM/PM - Name: message
    re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}\s*[AP]M)\s*-\s*([^:]+):\s*(.+)$", re.IGNORECASE),
]


class WhatsAppAnalyzer:
    def _parse_line(self, line: str) -> Optional[Tuple[str, str, str]]:
        for pattern in FORMATS:
            m = pattern.match(line.strip())
            if m:
                date_str, time_str, sender, content = m.groups()
                sender = sender.strip()
                content = content.strip()

                if any(re.search(p, content.lower()) for p in SYSTEM_MESSAGE_PATTERNS):
                    return None

                timestamp = f"{date_str} {time_str}"
                return sender, timestamp, content
        return None

    def _extract_hour(self, timestamp: str) -> Optional[int]:
        am_pm_match = re.search(r"(\d{1,2}):(\d{2})(?::\d{2})?\s*([AP]M)", timestamp, re.IGNORECASE)
        if am_pm_match:
            hour = int(am_pm_match.group(1))
            minute = int(am_pm_match.group(2))
            meridiem = am_pm_match.group(3).upper()
            if meridiem == "PM" and hour != 12:
                hour += 12
            elif meridiem == "AM" and hour == 12:
                hour = 0
            return hour

        time_match = re.search(r"(\d{1,2}):(\d{2})", timestamp)
        if time_match:
            return int(time_match.group(1))
        return None

    def parse_chat(self, text_content: str) -> List[Dict[str, Any]]:
        messages = []
        lines = text_content.split("\n")
        current_message = None

        for line in lines:
            parsed = self._parse_line(line)
            if parsed:
                if current_message:
                    messages.append(current_message)
                sender, timestamp, content = parsed
                current_message = {
                    "sender": sender,
                    "timestamp": timestamp,
                    "content": content,
                    "hour": self._extract_hour(timestamp),
                }
            elif current_message and line.strip():
                current_message["content"] += " " + line.strip()

        if current_message:
            messages.append(current_message)

        return messages

    def analyze(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            return {
                "total_messages": 0,
                "unique_senders": 0,
                "sentiment_score": 50,
                "emotional_tone": "Neutral",
                "late_night_ratio": 0,
                "avg_messages_per_day": 0,
                "most_active_hours": [],
                "top_words": [],
                "isolation_score": 0,
                "message_frequency_trend": "stable",
                "insights": ["No messages found in the uploaded file."],
            }

        total = len(messages)
        senders = set(m["sender"] for m in messages)

        positive_count = 0
        negative_count = 0
        all_words = []

        for msg in messages:
            content_lower = msg["content"].lower()
            words = re.findall(r"\b\w+\b", content_lower)
            all_words.extend(words)

            for word in POSITIVE_WORDS:
                if word in content_lower:
                    positive_count += 1
                    break

            for emoji in POSITIVE_EMOJIS:
                if emoji in msg["content"]:
                    positive_count += 1
                    break

            for word in NEGATIVE_WORDS:
                if word in content_lower:
                    negative_count += 1
                    break

            for emoji in NEGATIVE_EMOJIS:
                if emoji in msg["content"]:
                    negative_count += 1
                    break

        total_sentiment = positive_count + negative_count
        if total_sentiment > 0:
            sentiment_score = round((positive_count / total_sentiment) * 100)
        else:
            sentiment_score = 50

        if sentiment_score >= 65:
            emotional_tone = "Positive"
        elif sentiment_score >= 50:
            emotional_tone = "Mostly Positive"
        elif sentiment_score >= 35:
            emotional_tone = "Mixed / Neutral"
        else:
            emotional_tone = "Mostly Negative"

        hour_counts: Dict[int, int] = {}
        late_night_count = 0
        for msg in messages:
            hour = msg.get("hour")
            if hour is not None:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
                if hour >= 23 or hour <= 3:
                    late_night_count += 1

        late_night_ratio = round(late_night_count / total, 3)

        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        most_active_hours = [f"{h}:00" for h, _ in sorted_hours[:3]]

        filtered_words = [w for w in all_words if w not in STOP_WORDS and len(w) > 2]
        word_freq = Counter(filtered_words)
        top_words = [{"word": w, "count": c} for w, c in word_freq.most_common(15)]

        date_pattern = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4})")
        date_set = set()
        for msg in messages:
            match = date_pattern.search(msg["timestamp"])
            if match:
                date_set.add(match.group(1))

        total_days = len(date_set)
        avg_messages_per_day = round(total / total_days, 1) if total_days > 0 else total

        first_half = messages[: total // 2]
        second_half = messages[total // 2 :]
        if len(second_half) > len(first_half) * 1.2:
            trend = "increasing"
        elif len(first_half) > len(second_half) * 1.2:
            trend = "decreasing"
        else:
            trend = "stable"

        isolation_score = 0
        if total_days > 7:
            active_days_ratio = min(total_days / 30, 1.0)
            isolation_score = round((1 - active_days_ratio) * 100)

        insights = []
        if late_night_ratio > 0.2:
            insights.append(f"High late-night messaging ({round(late_night_ratio * 100)}%) — may indicate sleep disruption.")
        if sentiment_score < 40:
            insights.append("Overall negative sentiment detected — emotional support may be helpful.")
        if sentiment_score > 70:
            insights.append("Strong positive communication patterns detected.")
        if isolation_score > 50:
            insights.append("Low messaging frequency suggests possible social withdrawal.")
        if avg_messages_per_day < 5:
            insights.append("Low daily communication — consider maintaining social connections.")
        if trend == "decreasing":
            insights.append("Declining communication frequency over time.")
        if trend == "increasing":
            insights.append("Increasing social engagement — positive sign.")
        if not insights:
            insights.append("Communication patterns appear healthy and balanced.")

        return {
            "total_messages": total,
            "unique_senders": len(senders),
            "sentiment_score": sentiment_score,
            "emotional_tone": emotional_tone,
            "late_night_ratio": late_night_ratio,
            "avg_messages_per_day": avg_messages_per_day,
            "most_active_hours": most_active_hours,
            "top_words": top_words,
            "isolation_score": isolation_score,
            "message_frequency_trend": trend,
            "total_days_active": total_days,
            "insights": insights,
        }
