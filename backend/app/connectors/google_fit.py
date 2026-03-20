import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

from ..core.config import settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_FIT_API = "https://www.googleapis.com/fitness/v1/users/me"

FIT_SCOPES = [
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.heart_rate.read",
    "https://www.googleapis.com/auth/fitness.body.read",
    "https://www.googleapis.com/auth/fitness.sleep.read",
]


class GoogleFitConnector:

    def __init__(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token

    def get_auth_url(self, user_id: str) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_FIT_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(FIT_SCOPES),
            "access_type": "offline",
            "state": user_id,
            "prompt": "consent",
        }
        return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_FIT_REDIRECT_URI,
                },
            )
            return resp.json()

    async def refresh_access_token(self) -> bool:
        if not self.refresh_token:
            return False
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            data = resp.json()
            if "access_token" in data:
                self.access_token = data["access_token"]
                return True
        return False

    async def _aggregate(self, data_type: str, days: int = 7) -> Dict[str, Any]:
        end_ms = int(time.time() * 1000)
        start_ms = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

        body = {
            "aggregateBy": [{"dataTypeName": data_type}],
            "bucketByTime": {"durationMillis": 86400000},
            "startTimeMillis": start_ms,
            "endTimeMillis": end_ms,
        }

        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GOOGLE_FIT_API}/dataset:aggregate",
                headers=headers,
                json=body,
                timeout=15,
            )
            if resp.status_code == 401 and self.refresh_token:
                if await self.refresh_access_token():
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    resp = await client.post(
                        f"{GOOGLE_FIT_API}/dataset:aggregate",
                        headers=headers,
                        json=body,
                        timeout=15,
                    )
            resp.raise_for_status()
            return resp.json()

    def _extract_daily_values(self, response: Dict) -> List[Dict]:
        buckets = response.get("bucket", [])
        daily = []
        for bucket in buckets:
            date_ms = int(bucket.get("startTimeMillis", 0))
            date = datetime.fromtimestamp(date_ms / 1000).strftime("%Y-%m-%d")
            value = 0
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    vals = point.get("value", [])
                    if vals:
                        v = vals[0]
                        value += v.get("intVal", 0) or int(v.get("fpVal", 0))
            daily.append({"date": date, "value": value})
        return daily

    async def get_steps(self, days: int = 7) -> List[Dict]:
        try:
            data = await self._aggregate("com.google.step_count.delta", days)
            return self._extract_daily_values(data)
        except Exception as e:
            print(f"[GoogleFit] Steps error: {e}")
            return []

    async def get_active_minutes(self, days: int = 7) -> List[Dict]:
        try:
            data = await self._aggregate("com.google.active_minutes", days)
            return self._extract_daily_values(data)
        except Exception as e:
            print(f"[GoogleFit] Active minutes error: {e}")
            return []

    async def get_calories(self, days: int = 7) -> List[Dict]:
        try:
            data = await self._aggregate("com.google.calories.expended", days)
            return self._extract_daily_values(data)
        except Exception as e:
            print(f"[GoogleFit] Calories error: {e}")
            return []

    async def get_heart_rate(self, days: int = 7) -> List[Dict]:
        try:
            data = await self._aggregate("com.google.heart_rate.bpm", days)
            return self._extract_daily_values(data)
        except Exception as e:
            print(f"[GoogleFit] Heart rate error: {e}")
            return []

    async def get_sleep(self, days: int = 7) -> List[Dict]:
        try:
            data = await self._aggregate("com.google.sleep.segment", days)
            return self._extract_daily_values(data)
        except Exception as e:
            print(f"[GoogleFit] Sleep error: {e}")
            return []

    async def get_full_analysis(self) -> Dict[str, Any]:
        steps_data      = await self.get_steps(7)
        active_data     = await self.get_active_minutes(7)
        calories_data   = await self.get_calories(7)
        heart_rate_data = await self.get_heart_rate(7)
        sleep_data      = await self.get_sleep(7)

        # Steps analysis (target: 10,000/day)
        steps_values = [d["value"] for d in steps_data if d["value"] > 0]
        avg_steps = round(sum(steps_values) / len(steps_values)) if steps_values else 0
        steps_score = min(100, round((avg_steps / 10000) * 100))

        # Active minutes (target: 30/day)
        active_values = [d["value"] for d in active_data if d["value"] > 0]
        avg_active = round(sum(active_values) / len(active_values)) if active_values else 0
        active_score = min(100, round((avg_active / 30) * 100))

        # Calories
        cal_values = [d["value"] for d in calories_data if d["value"] > 0]
        avg_calories = round(sum(cal_values) / len(cal_values)) if cal_values else 0

        # Heart rate
        hr_values = [d["value"] for d in heart_rate_data if d["value"] > 0]
        avg_hr = round(sum(hr_values) / len(hr_values)) if hr_values else 0
        # Resting HR score: 60-70 bpm is excellent, >100 is poor
        if avg_hr == 0:
            hr_score = 50
        elif avg_hr < 60:
            hr_score = 90
        elif avg_hr <= 70:
            hr_score = 100
        elif avg_hr <= 80:
            hr_score = 80
        elif avg_hr <= 90:
            hr_score = 65
        elif avg_hr <= 100:
            hr_score = 50
        else:
            hr_score = 30

        # Overall fitness score
        active_sources = sum([
            1 if steps_values else 0,
            1 if active_values else 0,
            1 if hr_values else 0,
        ])

        if active_sources == 0:
            fitness_score = 50.0
        else:
            scores = []
            if steps_values: scores.append(steps_score)
            if active_values: scores.append(active_score)
            if hr_values: scores.append(hr_score)
            fitness_score = round(sum(scores) / len(scores), 1)

        # Trend: compare first 3 vs last 3 days
        if len(steps_values) >= 6:
            first_half = sum(steps_values[:3]) / 3
            second_half = sum(steps_values[-3:]) / 3
            if second_half > first_half * 1.1:
                activity_trend = "improving"
            elif second_half < first_half * 0.9:
                activity_trend = "declining"
            else:
                activity_trend = "stable"
        else:
            activity_trend = "stable"

        # Insights
        insights = []
        if avg_steps > 0:
            if avg_steps >= 10000:
                insights.append({"type": "positive", "message": f"✅ Excellent! Averaging {avg_steps:,} steps/day — above the 10,000 step goal."})
            elif avg_steps >= 7500:
                insights.append({"type": "info", "message": f"👟 Good activity — {avg_steps:,} steps/day. Try to reach 10,000 for optimal wellness."})
            else:
                insights.append({"type": "warning", "message": f"⚠️ Low step count ({avg_steps:,}/day). Aim for 10,000 steps to boost mental wellness."})

        if avg_active > 0:
            if avg_active >= 30:
                insights.append({"type": "positive", "message": f"✅ Great! {avg_active} active minutes/day meets the recommended 30-min guideline."})
            else:
                insights.append({"type": "warning", "message": f"⚠️ Only {avg_active} active minutes/day. 30+ minutes of daily activity improves mood significantly."})

        if avg_hr > 0:
            if avg_hr <= 70:
                insights.append({"type": "positive", "message": f"❤️ Healthy resting heart rate ({avg_hr} bpm) — good cardiovascular fitness."})
            elif avg_hr > 90:
                insights.append({"type": "warning", "message": f"⚠️ Elevated heart rate ({avg_hr} bpm) may indicate stress or low fitness. Consider cardio exercise."})

        if activity_trend == "improving":
            insights.append({"type": "positive", "message": "📈 Your activity level is trending upward — great momentum!"})
        elif activity_trend == "declining":
            insights.append({"type": "warning", "message": "📉 Activity declining over the past week — try to stay consistent."})

        if not insights:
            insights.append({"type": "info", "message": "Connect Google Fit and start moving to see personalized insights."})

        return {
            "fitness_score": fitness_score,
            "steps_score": steps_score,
            "active_minutes_score": active_score,
            "heart_rate_score": hr_score,
            "avg_daily_steps": avg_steps,
            "avg_active_minutes": avg_active,
            "avg_calories": avg_calories,
            "avg_heart_rate": avg_hr,
            "activity_trend": activity_trend,
            "steps_data": steps_data,
            "active_minutes_data": active_data,
            "calories_data": calories_data,
            "heart_rate_data": heart_rate_data,
            "days_analyzed": 7,
            "insights": insights,
        }
