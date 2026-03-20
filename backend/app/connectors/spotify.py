import urllib.parse
from typing import Any, Dict, List, Optional

import httpx

from ..core.config import settings

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

SPOTIFY_SCOPES = [
    "user-read-recently-played",
    "user-top-read",
    "user-read-playback-state",
    "user-library-read",
    "playlist-read-private",
]


class SpotifyConnector:
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token

    def get_auth_url(self, user_id: str) -> str:
        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "scope": " ".join(SPOTIFY_SCOPES),
            "state": user_id,
        }
        return f"{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}"

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        import base64
        credentials = base64.b64encode(
            f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                SPOTIFY_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
                },
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            return response.json()

    async def _api_get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SPOTIFY_API_BASE}{endpoint}",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params=params or {},
            )
            response.raise_for_status()
            return response.json()

    async def get_recently_played(self, limit: int = 50) -> List[Dict[str, Any]]:
        data = await self._api_get("/me/player/recently-played", {"limit": limit})
        return data.get("items", [])

    async def get_top_tracks(self, time_range: str = "short_term") -> List[Dict[str, Any]]:
        data = await self._api_get("/me/top/tracks", {"time_range": time_range, "limit": 50})
        return data.get("items", [])

    async def get_audio_features(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        if not track_ids:
            return []

        batch_size = 100
        all_features = []

        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i : i + batch_size]
            try:
                data = await self._api_get("/audio-features", {"ids": ",".join(batch)})
                features = data.get("audio_features", [])
                print(f"[Spotify] Fetched audio features for {len(batch)} tracks, got {len(features)} results")
                all_features.extend(features)
            except Exception as e:
                print(f"[Spotify] Audio features error: {e}")

        return all_features

    def _get_emotional_tone(self, valence: float, energy: float) -> str:
        if valence >= 0.6 and energy >= 0.6:
            return "Happy & Energetic"
        elif valence >= 0.6 and energy < 0.4:
            return "Content & Calm"
        elif valence < 0.4 and energy >= 0.6:
            return "Angry & Agitated"
        elif valence < 0.4 and energy < 0.4:
            return "Sad & Low Energy"
        elif valence < 0.5 and energy >= 0.4:
            return "Melancholic"
        else:
            return "Neutral"

    async def get_full_analysis(self) -> Dict[str, Any]:
        recently_played = await self.get_recently_played(limit=50)
        top_tracks = await self.get_top_tracks(time_range="short_term")

        track_ids = []
        seen = set()
        for item in recently_played:
            tid = item.get("track", {}).get("id")
            if tid and tid not in seen:
                seen.add(tid)
                track_ids.append(tid)

        audio_features = await self.get_audio_features(track_ids[:50])
        valid_features = [f for f in audio_features if f and f.get("valence") is not None]

        if valid_features:
            avg_valence = sum(f["valence"] for f in valid_features) / len(valid_features)
            avg_energy = sum(f["energy"] for f in valid_features) / len(valid_features)
            avg_tempo = sum(f["tempo"] for f in valid_features) / len(valid_features)
            avg_danceability = sum(f["danceability"] for f in valid_features) / len(valid_features)
        else:
            print("[Spotify] No valid audio features found, using fallback values")
            avg_valence = 0.45
            avg_energy = 0.55
            avg_tempo = 120.0
            avg_danceability = 0.50

        late_night_count = 0
        total_played = len(recently_played)
        for item in recently_played:
            played_at = item.get("played_at", "")
            if played_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(played_at.replace("Z", "+00:00"))
                    hour = dt.hour
                    if hour >= 23 or hour <= 4:
                        late_night_count += 1
                except Exception:
                    pass

        late_night_ratio = late_night_count / total_played if total_played > 0 else 0.0
        emotional_tone = self._get_emotional_tone(avg_valence, avg_energy)

        recent_tracks_formatted = []
        for item in recently_played[:10]:
            track = item.get("track", {})
            recent_tracks_formatted.append({
                "name": track.get("name", "Unknown"),
                "artist": ", ".join(a["name"] for a in track.get("artists", [])),
                "album": track.get("album", {}).get("name", ""),
                "album_art": (track.get("album", {}).get("images") or [{}])[0].get("url", ""),
                "played_at": item.get("played_at", ""),
            })

        top_tracks_formatted = []
        for track in top_tracks[:10]:
            top_tracks_formatted.append({
                "name": track.get("name", "Unknown"),
                "artist": ", ".join(a["name"] for a in track.get("artists", [])),
                "album_art": (track.get("album", {}).get("images") or [{}])[0].get("url", ""),
            })

        mood_score = round(avg_valence * 100)

        return {
            "mood_score": mood_score,
            "emotional_tone": emotional_tone,
            "avg_valence": round(avg_valence, 3),
            "avg_energy": round(avg_energy, 3),
            "avg_tempo": round(avg_tempo, 1),
            "avg_danceability": round(avg_danceability, 3),
            "late_night_ratio": round(late_night_ratio, 3),
            "total_tracks_analyzed": total_played,
            "recently_played": recent_tracks_formatted,
            "top_tracks": top_tracks_formatted,
            "features_analyzed": len(valid_features),
        }

    async def refresh_access_token(self, refresh_token: str) -> dict:
        import base64
        credentials = base64.b64encode(
            f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SPOTIFY_TOKEN_URL,
                data={"grant_type": "refresh_token", "refresh_token": refresh_token},
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            return response.json()
