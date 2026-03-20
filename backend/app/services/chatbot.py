from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from ..core.config import settings


class MindWatchChatbot:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-flash-lite-latest"

    def build_context(
        self,
        spotify_data: Optional[Dict[str, Any]],
        youtube_data: Optional[Dict[str, Any]],
        whatsapp_data: Optional[Dict[str, Any]],
    ) -> str:
        context_parts = []

        if spotify_data:
            context_parts.append(f"""
SPOTIFY MUSIC DATA:
- Emotional Tone: {spotify_data.get('emotional_tone', 'Unknown')}
- Mood Score: {spotify_data.get('mood_score', 'N/A')}/100
- Average Valence (happiness): {spotify_data.get('avg_valence', 'N/A')}
- Average Energy: {spotify_data.get('avg_energy', 'N/A')}
- Average Tempo (BPM): {spotify_data.get('avg_tempo', 'N/A')}
- Late Night Listening Ratio: {round(spotify_data.get('late_night_ratio', 0) * 100)}%
- Tracks Analyzed: {spotify_data.get('total_tracks_analyzed', 0)}
""")

        if youtube_data:
            context_parts.append(f"""
YOUTUBE CONSUMPTION DATA:
- Emotional Diet Score: {youtube_data.get('emotional_diet_score', 'N/A')}/100
- Content Mood: {youtube_data.get('content_mood', 'Unknown')}
- Dark Content Percentage: {youtube_data.get('dark_content_percentage', 0)}%
- Recovery Score: {youtube_data.get('recovery_score', 'N/A')}
- Rumination Score: {youtube_data.get('rumination_score', 'N/A')}
- Category Breakdown: {youtube_data.get('category_breakdown', {})}
- Insights: {'; '.join(youtube_data.get('insights', []))}
""")

        if whatsapp_data:
            context_parts.append(f"""
WHATSAPP COMMUNICATION DATA:
- Total Messages: {whatsapp_data.get('total_messages', 0)}
- Sentiment Score: {whatsapp_data.get('sentiment_score', 'N/A')}/100
- Emotional Tone: {whatsapp_data.get('emotional_tone', 'Unknown')}
- Late Night Messaging: {round(whatsapp_data.get('late_night_ratio', 0) * 100)}%
- Avg Messages per Day: {whatsapp_data.get('avg_messages_per_day', 0)}
- Message Trend: {whatsapp_data.get('message_frequency_trend', 'stable')}
- Isolation Score: {whatsapp_data.get('isolation_score', 0)}/100
- Insights: {'; '.join(whatsapp_data.get('insights', []))}
""")

        if not context_parts:
            return "No data sources connected yet. Provide general mental wellness guidance."

        return "\n".join(context_parts)

    async def chat(
        self,
        message: str,
        history: List[Dict[str, str]],
        spotify_data: Optional[Dict[str, Any]] = None,
        youtube_data: Optional[Dict[str, Any]] = None,
        whatsapp_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        try:
            context = self.build_context(spotify_data, youtube_data, whatsapp_data)

            system_instruction = f"""You are MindWatch AI, a compassionate and insightful mental wellness assistant. You analyze users' digital behavior data to provide personalized mental health insights.

Your role:
- Be warm, empathetic, and non-judgmental
- Provide actionable, evidence-based wellness advice
- Reference the user's actual data when relevant
- Never diagnose conditions — always suggest professional help for serious concerns
- Keep responses concise (2-4 paragraphs max) and conversational

USER'S CURRENT DATA:
{context}

Important: You are NOT a medical professional. Always recommend consulting a healthcare provider for clinical concerns."""

            contents = []
            for h in history[-10:]:
                if h.get("message"):
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[types.Part(text=h["message"])],
                        )
                    )
                if h.get("response"):
                    contents.append(
                        types.Content(
                            role="model",
                            parts=[types.Part(text=h["response"])],
                        )
                    )

            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=message)],
                )
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=512,
                    temperature=0.7,
                ),
            )

            return response.text

        except Exception as e:
            return f"I'm having trouble processing your request right now. Please try again in a moment. (Error: {str(e)[:100]})"
