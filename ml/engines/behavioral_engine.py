from datetime import datetime
from typing import Optional


class BehavioralEngine:

    def analyze_spotify_behavior(self, recently_played: list) -> dict:
        if not recently_played:
            return self._empty_result()

        hours = []
        for item in recently_played:
            played_at = item.get('played_at', '')
            if played_at:
                try:
                    hour = datetime.fromisoformat(
                        played_at.replace('Z', '+00:00')
                    ).hour
                    hours.append(hour)
                except Exception:
                    pass

        if not hours:
            return self._empty_result()

        total = len(hours)
        late_night = sum(1 for h in hours if 0 <= h <= 4 or h >= 23)
        morning = sum(1 for h in hours if 6 <= h <= 9)

        late_night_ratio = late_night / total
        morning_ratio = morning / total

        try:
            import statistics
            consistency = 1 - (statistics.stdev(hours) / 12)
            consistency = max(0, min(1, consistency))
        except Exception:
            consistency = 0.5

        behavioral_score = 60.0
        if late_night_ratio > 0.4:
            behavioral_score -= 25
        elif late_night_ratio > 0.2:
            behavioral_score -= 10
        if morning_ratio > 0.2:
            behavioral_score += 10
        if consistency > 0.7:
            behavioral_score += 10
        elif consistency < 0.3:
            behavioral_score -= 10

        behavioral_score = max(0, min(100, behavioral_score))

        signals = []
        if late_night_ratio > 0.3:
            signals.append(f"⚠️ {round(late_night_ratio*100)}% of listening is late night (11pm-4am)")
        if morning_ratio > 0.2:
            signals.append("✅ Good morning listening habit detected")
        if consistency < 0.3:
            signals.append("⚠️ Very irregular listening patterns detected")

        return {
            'behavioral_score': round(behavioral_score, 1),
            'late_night_ratio': round(late_night_ratio, 3),
            'morning_ratio': round(morning_ratio, 3),
            'consistency_score': round(consistency * 100, 1),
            'sleep_disruption_score': round(late_night_ratio * 100, 1),
            'total_plays_analyzed': total,
            'behavioral_signals': signals,
        }

    def analyze_message_behavior(self, messages: list) -> dict:
        if not messages:
            return {
                'late_night_messaging_ratio': 0,
                'avg_messages_per_day': 0,
                'message_behavior_score': 50,
            }

        hours = [m.get('hour', 0) for m in messages]
        total = len(messages)
        late_night = sum(1 for h in hours if 0 <= h <= 4 or h >= 23)
        late_night_ratio = late_night / total if total > 0 else 0

        return {
            'late_night_messaging_ratio': round(late_night_ratio, 3),
            'total_messages': total,
            'message_behavior_score': round(max(0, 70 - late_night_ratio * 40), 1),
        }

    def compute_behavioral_score(
        self,
        spotify_behavior: Optional[dict] = None,
        message_behavior: Optional[dict] = None,
    ) -> dict:
        scores = []
        signals = []

        if spotify_behavior:
            scores.append(spotify_behavior.get('behavioral_score', 50))
            signals.extend(spotify_behavior.get('behavioral_signals', []))

        if message_behavior:
            scores.append(message_behavior.get('message_behavior_score', 50))

        final_score = sum(scores) / len(scores) if scores else 50.0

        return {
            'behavioral_score': round(final_score, 1),
            'sleep_disruption_score': spotify_behavior.get('sleep_disruption_score', 0) if spotify_behavior else 0,
            'consistency_score': spotify_behavior.get('consistency_score', 50) if spotify_behavior else 50,
            'late_night_activity': spotify_behavior.get('late_night_ratio', 0) if spotify_behavior else 0,
            'behavioral_signals': signals,
        }

    def _empty_result(self) -> dict:
        return {
            'behavioral_score': 50.0,
            'late_night_ratio': 0,
            'morning_ratio': 0,
            'consistency_score': 50,
            'sleep_disruption_score': 0,
            'total_plays_analyzed': 0,
            'behavioral_signals': [],
        }
