import os
import sys
from typing import Optional

MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../models/bert_emotion_classifier')
)

_bert_model = None
_bert_tokenizer = None
BERT_AVAILABLE = False


def _load_bert():
    global _bert_model, _bert_tokenizer, BERT_AVAILABLE
    if BERT_AVAILABLE:
        return True
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        if not os.path.exists(MODEL_PATH):
            print(f"BERT model not found at {MODEL_PATH}")
            return False
        print(f"Loading BERT from {MODEL_PATH}...")
        _bert_tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        _bert_model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        _bert_model.eval()
        BERT_AVAILABLE = True
        print("✅ BERT emotion model loaded!")
        return True
    except Exception as e:
        print(f"BERT load failed: {e} — using VADER fallback")
        return False


try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
except Exception:
    VADER_AVAILABLE = False

LABELS = ['sadness', 'joy', 'love', 'anger', 'fear', 'surprise']

POSITIVE_EMOTIONS = {'joy', 'love', 'surprise'}
NEGATIVE_EMOTIONS = {'sadness', 'anger', 'fear'}

EMOTION_SCORE_MAP = {
    'joy':      0.85,
    'love':     0.90,
    'surprise': 0.55,
    'anger':   -0.60,
    'fear':    -0.65,
    'sadness': -0.75,
}


class LinguisticEngine:

    def __init__(self):
        _load_bert()

    def analyze_text(self, text: str) -> dict:
        if not text or len(text.strip()) < 3:
            return {'emotion': 'neutral', 'confidence': 0.5, 'sentiment_score': 0.5}

        if BERT_AVAILABLE:
            return self._bert_analyze(text)
        return self._vader_analyze(text)

    def _bert_analyze(self, text: str) -> dict:
        try:
            import torch
            inputs = dict(_bert_tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=128,
                padding=True,
            ))
            inputs.pop('token_type_ids', None)  # DistilBERT does not accept token_type_ids
            with torch.no_grad():
                outputs = _bert_model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)[0]

            pred_idx = probs.argmax().item()
            emotion = LABELS[pred_idx]
            confidence = float(probs[pred_idx])
            sentiment_score = (EMOTION_SCORE_MAP.get(emotion, 0) + 1) / 2

            return {
                'emotion': emotion,
                'confidence': round(confidence, 3),
                'sentiment_score': round(sentiment_score, 3),
                'all_emotions': {
                    LABELS[i]: round(float(probs[i]), 3)
                    for i in range(len(LABELS))
                },
                'method': 'bert',
            }
        except Exception as e:
            print(f"BERT inference error: {e}")
            return self._vader_analyze(text)

    def _vader_analyze(self, text: str) -> dict:
        if VADER_AVAILABLE:
            scores = _vader.polarity_scores(text)
            compound = scores['compound']
            sentiment_score = (compound + 1) / 2

            if compound >= 0.5:
                emotion = 'joy'
            elif compound >= 0.1:
                emotion = 'love'
            elif compound <= -0.5:
                emotion = 'sadness'
            elif compound <= -0.1:
                emotion = 'fear'
            else:
                emotion = 'surprise'
        else:
            sentiment_score = 0.5
            emotion = 'surprise'

        return {
            'emotion': emotion,
            'confidence': 0.6,
            'sentiment_score': round(sentiment_score, 3),
            'method': 'vader_fallback',
        }

    def analyze_messages(self, messages: list) -> dict:
        if not messages:
            return self._empty_result()

        sample = messages[-200:] if len(messages) > 200 else messages
        results = [self.analyze_text(str(m)) for m in sample if m]

        if not results:
            return self._empty_result()

        emotion_counts = {}
        sentiment_scores = []
        for r in results:
            emotion = r.get('emotion', 'surprise')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            sentiment_scores.append(r.get('sentiment_score', 0.5))

        total = len(results)
        emotion_distribution = {
            e: round(c / total, 3) for e, c in emotion_counts.items()
        }

        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

        mid = len(sentiment_scores) // 2
        if mid > 0:
            first_half = sum(sentiment_scores[:mid]) / mid
            second_half = sum(sentiment_scores[mid:]) / (len(sentiment_scores) - mid)
            if second_half > first_half + 0.05:
                trend = 'improving'
            elif second_half < first_half - 0.05:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'

        crisis_emotions = (
            emotion_distribution.get('fear', 0) +
            emotion_distribution.get('sadness', 0)
        )

        linguistic_score = self._compute_score(
            emotion_distribution, avg_sentiment, crisis_emotions
        )

        dominant = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'surprise'

        return {
            'linguistic_score': round(linguistic_score, 1),
            'dominant_emotion': dominant,
            'emotion_distribution': emotion_distribution,
            'avg_sentiment': round(avg_sentiment, 3),
            'sentiment_trend': trend,
            'crisis_signals': round(crisis_emotions, 3),
            'messages_analyzed': total,
            'method_used': 'bert' if BERT_AVAILABLE else 'vader_fallback',
        }

    def _compute_score(
        self,
        emotion_dist: dict,
        avg_sentiment: float,
        crisis_signals: float,
    ) -> float:
        base = avg_sentiment * 100
        positive_boost = (
            emotion_dist.get('joy', 0) * 20 +
            emotion_dist.get('love', 0) * 15
        )
        negative_penalty = (
            emotion_dist.get('sadness', 0) * 25 +
            emotion_dist.get('fear', 0) * 20 +
            emotion_dist.get('anger', 0) * 15
        )
        crisis_penalty = crisis_signals * 30
        score = base + positive_boost - negative_penalty - crisis_penalty
        return max(0, min(100, score))

    def _empty_result(self) -> dict:
        return {
            'linguistic_score': 50.0,
            'dominant_emotion': 'neutral',
            'emotion_distribution': {},
            'avg_sentiment': 0.5,
            'sentiment_trend': 'stable',
            'crisis_signals': 0.0,
            'messages_analyzed': 0,
            'method_used': 'none',
        }
