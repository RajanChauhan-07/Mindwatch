import os
import sys
from datetime import datetime
from typing import Optional

ML_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../../ml')
)
if ML_PATH not in sys.path:
    sys.path.insert(0, ML_PATH)

_linguistic = None
_consumption = None
_behavioral = None
_fuzzy = None
_predictor = None


def _get_engines():
    global _linguistic, _consumption, _behavioral, _fuzzy, _predictor
    if _linguistic is None:
        try:
            from engines.linguistic_engine import LinguisticEngine
            from engines.consumption_engine import ConsumptionEngine
            from engines.behavioral_engine import BehavioralEngine
            from engines.fuzzy_engine import FuzzyWellnessEngine
            from engines.predictor import WellnessPredictor

            _linguistic  = LinguisticEngine()
            _consumption = ConsumptionEngine()
            _behavioral  = BehavioralEngine()
            _fuzzy       = FuzzyWellnessEngine()
            _predictor   = WellnessPredictor()
            print("✅ All ML engines loaded!")
        except Exception as e:
            print(f"Engine load error: {e}")
    return _linguistic, _consumption, _behavioral, _fuzzy, _predictor


class WellnessPipeline:

    def __init__(self):
        _get_engines()

    async def analyze(
        self,
        spotify_data: Optional[dict] = None,
        youtube_data: Optional[dict] = None,
        whatsapp_data: Optional[dict] = None,
        historical_scores: Optional[list] = None,
    ) -> dict:
        linguistic_e, consumption_e, behavioral_e, fuzzy_e, predictor_e = _get_engines()

        linguistic_result  = None
        consumption_result = None
        behavioral_result  = None

        # Linguistic engine on WhatsApp messages
        if whatsapp_data and linguistic_e:
            try:
                messages = [m.get('content', '') for m in whatsapp_data.get('messages', [])]
                messages = [m for m in messages if m]
                if messages:
                    linguistic_result = linguistic_e.analyze_messages(messages)
            except Exception as e:
                print(f"Linguistic engine error: {e}")

        # Consumption engine on YouTube videos
        if (youtube_data or spotify_data) and consumption_e:
            try:
                videos = []
                if youtube_data:
                    videos = youtube_data.get('videos', [])
                    if not videos and youtube_data.get('recently_played'):
                        videos = [{'title': item.get('track', {}).get('name', '')}
                                  for item in youtube_data.get('recently_played', [])]
                consumption_result = consumption_e.analyze_consumption(videos, [])
            except Exception as e:
                print(f"Consumption engine error: {e}")

        # Fallback: use pre-analysed YouTube data
        if not consumption_result and youtube_data:
            consumption_result = {
                'consumption_score': youtube_data.get('emotional_diet_score', 50),
                'emotional_diet_score': youtube_data.get('emotional_diet_score', 50),
                'category_breakdown': youtube_data.get('category_breakdown', {}),
                'dark_content_percentage': youtube_data.get('dark_content_percentage', 0),
                'motivational_percentage': youtube_data.get('motivational_percentage', 0),
                'recovery_score': youtube_data.get('recovery_score', 0),
                'rumination_score': youtube_data.get('rumination_score', 0),
                'content_mood': youtube_data.get('content_mood', 'Unknown'),
                'insights': youtube_data.get('insights', []),
            }

        # Behavioral engine
        if spotify_data and behavioral_e:
            try:
                spotify_behavior = behavioral_e.analyze_spotify_behavior(
                    spotify_data.get('recently_played', [])
                )
                whatsapp_behavior = None
                if whatsapp_data:
                    whatsapp_behavior = behavioral_e.analyze_message_behavior(
                        whatsapp_data.get('messages', [])
                    )
                behavioral_result = behavioral_e.compute_behavioral_score(
                    spotify_behavior, whatsapp_behavior
                )
            except Exception as e:
                print(f"Behavioral engine error: {e}")

        # Fallback behavioral from Spotify
        if not behavioral_result and spotify_data:
            late_night = spotify_data.get('late_night_ratio', 0)
            behavioral_result = {
                'behavioral_score': max(0, min(100, 70 - late_night * 40)),
                'sleep_disruption_score': round(late_night * 100, 1),
                'consistency_score': 50,
                'late_night_activity': late_night,
                'behavioral_signals': [],
            }

        # Compute component scores with fallbacks
        linguistic_score  = linguistic_result['linguistic_score']  if linguistic_result  else 50.0
        consumption_score = consumption_result['consumption_score'] if consumption_result else 50.0
        behavioral_score  = behavioral_result['behavioral_score']  if behavioral_result  else 50.0

        # Use Spotify valence as linguistic proxy if no WhatsApp
        if not linguistic_result and spotify_data:
            valence = spotify_data.get('avg_valence', 0.5)
            linguistic_score = round(valence * 100, 1)

        # Fuzzy fusion
        fuzzy_result = None
        if fuzzy_e:
            try:
                fuzzy_result = fuzzy_e.compute_wellness(
                    linguistic_score, consumption_score, behavioral_score
                )
            except Exception as e:
                print(f"Fuzzy engine error: {e}")

        if not fuzzy_result:
            wellness_score = (linguistic_score * 0.40 +
                              consumption_score * 0.35 +
                              behavioral_score * 0.25)
            fuzzy_result = {
                'wellness_score': round(wellness_score, 1),
                'risk_level': self._get_risk_level(wellness_score),
                'explanation': 'Score computed using weighted average.',
                'input_scores': {
                    'linguistic': linguistic_score,
                    'consumption': consumption_score,
                    'behavioral': behavioral_score,
                },
                'method': 'weighted_average_fallback',
            }

        # Predictions
        predictions_result = {'available': False, 'predictions': []}
        if predictor_e and historical_scores:
            try:
                predictions_result = predictor_e.predict(historical_scores)
            except Exception as e:
                print(f"Predictor error: {e}")

        sources = []
        if spotify_data:  sources.append('spotify')
        if youtube_data:  sources.append('youtube')
        if whatsapp_data: sources.append('whatsapp')

        return {
            'overall_wellness_score': fuzzy_result['wellness_score'],
            'risk_level': fuzzy_result['risk_level'],
            'explanation': fuzzy_result['explanation'],
            'scores': {
                'linguistic':  round(linguistic_score, 1),
                'consumption': round(consumption_score, 1),
                'behavioral':  round(behavioral_score, 1),
                'fuzzy_output': fuzzy_result['wellness_score'],
            },
            'fuzzy_method': fuzzy_result.get('method', 'unknown'),
            'linguistic_details':  linguistic_result,
            'consumption_details': consumption_result,
            'behavioral_details':  behavioral_result,
            'predictions':         predictions_result,
            'data_sources_used':   sources,
            'analysis_timestamp':  datetime.utcnow().isoformat(),
        }

    def _get_risk_level(self, score: float) -> str:
        if score >= 80: return 'excellent'
        if score >= 65: return 'good'
        if score >= 45: return 'moderate'
        if score >= 30: return 'poor'
        return 'critical'
