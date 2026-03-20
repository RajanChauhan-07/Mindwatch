import re
import string
from datetime import datetime
from typing import Optional

STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
    'your', 'yours', 'yourself', 'he', 'him', 'his', 'himself', 'she',
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
    'their', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
    'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
    'the', 'a', 'an', 'and', 'but', 'if', 'or', 'as', 'at', 'by',
    'for', 'in', 'of', 'on', 'to', 'up', 'with', 'about', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'from',
    'ok', 'okay', 'yeah', 'yes', 'no', 'not', 'so', 'just', 'now',
    'like', 'get', 'got', 'also', 'even', 'well', 'still', 'back',
    'media', 'omitted', 'message', 'deleted', 'null', 'http', 'https',
    'www', 'com', 'will', 'oh', 'hi', 'hey', 'hello', 'lol', 'haha'
}


class TextPreprocessor:

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def extract_whatsapp_messages(self, raw_text: str) -> list:
        messages = []
        patterns = [
            r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\]\s*([^:]+):\s*(.+)',
            r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?:\s*[AP]M)?)\s*-\s*([^:]+):\s*(.+)',
            r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.+)',
        ]

        skip_phrases = [
            'messages and calls are end-to-end encrypted',
            '<media omitted>',
            'missed voice call',
            'missed video call',
            'this message was deleted',
            'you deleted this message',
            'null',
            'changed the subject',
            'added',
            'removed',
            'left',
            'changed this group',
            'created group',
            'security code changed',
        ]

        for line in raw_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            skip = False
            for phrase in skip_phrases:
                if phrase in line.lower():
                    skip = True
                    break
            if skip:
                continue

            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    date_str = groups[0]
                    time_str = groups[1]
                    sender = groups[2].strip()
                    content = groups[3].strip()

                    try:
                        hour = int(time_str.split(':')[0])
                        if 'PM' in time_str.upper() and hour != 12:
                            hour += 12
                        elif 'AM' in time_str.upper() and hour == 12:
                            hour = 0
                    except Exception:
                        hour = 0

                    messages.append({
                        'sender': sender,
                        'content': content,
                        'hour': hour,
                        'raw_time': time_str,
                    })
                    break

        return messages

    def get_top_words(self, messages: list, top_n: int = 20) -> list:
        word_count = {}
        for msg in messages:
            content = msg.get('content', '') if isinstance(msg, dict) else str(msg)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
            for word in words:
                if word not in STOPWORDS and len(word) > 2:
                    word_count[word] = word_count.get(word, 0) + 1

        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [{'word': w, 'count': c} for w, c in sorted_words[:top_n]]
