import os
import re
from collections import Counter
from typing import Optional

_ml_pipeline = None
ML_MODEL_AVAILABLE = False

MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../models/content_classifier.pkl')
)


def _load_model():
    global _ml_pipeline, ML_MODEL_AVAILABLE
    if ML_MODEL_AVAILABLE:
        return True
    try:
        import joblib
        if not os.path.exists(MODEL_PATH):
            return False
        _ml_pipeline = joblib.load(MODEL_PATH)
        ML_MODEL_AVAILABLE = True
        print("✅ Content classifier ML model loaded!")
        return True
    except Exception as e:
        print(f"Content classifier load failed: {e} — using keyword fallback")
        return False


CATEGORY_KEYWORDS = {
    'dark_content':   ['suicide', 'self harm', 'depression', 'hopeless', 'death', 'kill', 'murder', 'horror', 'abuse', 'trauma', 'breakdown', 'suffer', 'disturbing'],
    'motivational':   ['motivation', 'success', 'hustle', 'inspire', 'achieve', 'goal', 'growth', 'mindset', 'productivity', 'entrepreneur', 'discipline', 'winner'],
    'entertainment':  ['funny', 'comedy', 'meme', 'prank', 'reaction', 'vlog', 'challenge', 'viral', 'roast', 'shorts', 'compilation'],
    'educational':    ['tutorial', 'learn', 'course', 'explain', 'how to', 'study', 'lecture', 'science', 'math', 'history', 'coding', 'programming', 'ai', 'ml'],
    'music':          ['song', 'music', 'lyrics', 'album', 'artist', 'concert', 'playlist', 'beats', 'remix', 'cover', 'acoustic'],
    'romantic_sad':   ['breakup', 'heartbreak', 'sad song', 'missing', 'lonely', 'love story', 'emotional', 'crying', 'tears', 'hurt', 'goodbye'],
    'gaming':         ['gameplay', 'gaming', 'playthrough', 'walkthrough', 'esports', 'minecraft', 'fortnite', 'pubg', 'valorant', 'gta'],
    'news':           ['news', 'politics', 'government', 'election', 'war', 'economy', 'breaking', 'update', 'world'],
    'spiritual':      ['meditation', 'yoga', 'spiritual', 'mindfulness', 'peace', 'calm', 'healing', 'manifest', 'gratitude'],
    'fitness':        ['workout', 'fitness', 'gym', 'exercise', 'diet', 'weight loss', 'muscle', 'training', 'health'],
}

CATEGORY_SENTIMENT = {
    'dark_content':  -0.90,
    'romantic_sad':  -0.60,
    'news':          -0.30,
    'gaming':         0.00,
    'entertainment':  0.35,
    'music':          0.20,
    'educational':    0.40,
    'motivational':   0.85,
    'spiritual':      0.65,
    'fitness':        0.55,
    'uncategorized':  0.00,
}


class ConsumptionEngine:

    def __init__(self):
        _load_model()

    def classify_content(self, title: str) -> tuple:
        if ML_MODEL_AVAILABLE:
            try:
                proba = _ml_pipeline.predict_proba([title])[0]
                pred = _ml_pipeline.predict([title])[0]
                confidence = max(proba)
                return pred, float(confidence)
            except Exception:
                pass
        return self._keyword_classify(title)

    def _keyword_classify(self, title: str) -> tuple:
        title_lower = title.lower()
        scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in title_lower)
            if score > 0:
                scores[category] = score
        if not scores:
            return 'uncategorized', 0.5
        best = max(scores, key=scores.get)
        return best, 0.7

    def analyze_consumption(self, videos: list, searches: list) -> dict:
        all_items = []
        for v in videos:
            title = v.get('title', '') if isinstance(v, dict) else str(v)
            if title:
                cat, conf = self.classify_content(title)
                all_items.append({'title': title, 'category': cat, 'confidence': conf})

        if not all_items:
            return self._empty_result()

        total = len(all_items)
        cat_counts = Counter(item['category'] for item in all_items)

        category_percentages = {
            cat: round((count / total) * 100, 1)
            for cat, count in cat_counts.most_common()
        }

        sentiment_scores = [
            CATEGORY_SENTIMENT.get(item['category'], 0)
            for item in all_items
        ]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        emotional_diet_score = round((avg_sentiment + 1) / 2 * 100, 1)

        dark_pct = category_percentages.get('dark_content', 0)
        motivational_pct = category_percentages.get('motivational', 0)

        recovery_score = round(
            motivational_pct +
            category_percentages.get('spiritual', 0) +
            category_percentages.get('fitness', 0), 1
        )
        rumination_score = round(
            dark_pct +
            category_percentages.get('romantic_sad', 0), 1
        )

        if dark_pct > 20:
            content_mood = 'Concerning — High dark content consumption'
        elif emotional_diet_score > 65:
            content_mood = 'Positive — Mostly uplifting content'
        elif emotional_diet_score > 45:
            content_mood = 'Neutral — Balanced content diet'
        else:
            content_mood = 'Heavy — Emotionally draining content patterns'

        insights = self._generate_insights(
            dark_pct, emotional_diet_score,
            category_percentages, recovery_score, rumination_score,
        )

        return {
            'consumption_score': emotional_diet_score,
            'emotional_diet_score': emotional_diet_score,
            'category_breakdown': category_percentages,
            'dark_content_percentage': dark_pct,
            'motivational_percentage': motivational_pct,
            'recovery_score': recovery_score,
            'rumination_score': rumination_score,
            'content_mood': content_mood,
            'total_videos_analyzed': total,
            'insights': insights,
            'method_used': 'ml_model' if ML_MODEL_AVAILABLE else 'keyword_fallback',
        }

    def _generate_insights(self, dark_pct, diet_score, categories, recovery, rumination):
        insights = []
        if dark_pct > 20:
            insights.append({'type': 'warning', 'message': f'⚠️ {dark_pct}% dark content detected. This can significantly impact your mood.'})
        if categories.get('romantic_sad', 0) > 15:
            insights.append({'type': 'warning', 'message': '💔 High sad/romantic content may indicate emotional rumination.'})
        if categories.get('motivational', 0) > 20:
            insights.append({'type': 'positive', 'message': '💪 Great motivational content consumption!'})
        if categories.get('educational', 0) > 25:
            insights.append({'type': 'positive', 'message': '📚 Strong educational content supports mental wellness.'})
        if recovery > rumination:
            insights.append({'type': 'positive', 'message': f'✅ Recovery content ({recovery:.0f}%) outweighs rumination content ({rumination:.0f}%). Healthy pattern!'})
        elif rumination > recovery:
            insights.append({'type': 'warning', 'message': f'⚠️ Rumination ({rumination:.0f}%) outweighs recovery content ({recovery:.0f}%). Consider more uplifting content.'})
        if diet_score > 65:
            insights.append({'type': 'positive', 'message': f'🌟 Emotional diet score: {diet_score}/100 — Your content choices support positive mental health.'})
        return insights

    def _empty_result(self):
        return {
            'consumption_score': 50.0,
            'emotional_diet_score': 50.0,
            'category_breakdown': {},
            'dark_content_percentage': 0,
            'motivational_percentage': 0,
            'recovery_score': 0,
            'rumination_score': 0,
            'content_mood': 'No data',
            'total_videos_analyzed': 0,
            'insights': [],
            'method_used': 'none',
        }
