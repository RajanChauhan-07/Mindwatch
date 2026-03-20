import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup


class YouTubeAnalyzer:
    CATEGORY_KEYWORDS: Dict[str, List[str]] = {
        "dark_content": [
            "murder", "death", "crime", "conspiracy", "suicide", "horror", "scary", "creepy",
            "disturbing", "tragic", "disaster", "attack", "violence", "war", "shooting",
            "abuse", "hate", "protest", "riot", "drug", "overdose",
        ],
        "motivational": [
            "motivation", "inspire", "success", "hustle", "grind", "achieve", "goal",
            "mindset", "growth", "discipline", "productivity", "focus", "morning routine",
            "self improvement", "entrepreneur", "startup", "habit",
        ],
        "entertainment": [
            "funny", "comedy", "prank", "challenge", "vlog", "reaction", "meme",
            "compilation", "highlights", "roast", "try not to laugh", "unboxing",
        ],
        "educational": [
            "tutorial", "how to", "learn", "course", "lecture", "explained", "science",
            "history", "documentary", "analysis", "review", "guide", "tips", "advice",
        ],
        "music": [
            "music", "song", "official", "lyrics", "mv", "album", "playlist", "acoustic",
            "cover", "remix", "live", "concert", "piano", "guitar",
        ],
        "romantic_sad": [
            "love", "heartbreak", "miss you", "breakup", "lonely", "sad song", "crying",
            "emotional", "feelings", "relationship", "romance", "dating",
        ],
        "gaming": [
            "gameplay", "gaming", "playthrough", "lets play", "walkthrough", "speedrun",
            "fortnite", "minecraft", "roblox", "valorant", "gta", "esports",
        ],
        "news": [
            "news", "breaking", "update", "report", "analysis", "politics", "election",
            "economy", "policy", "government", "president", "minister",
        ],
        "spiritual": [
            "meditation", "spiritual", "yoga", "mindfulness", "prayer", "god", "faith",
            "healing", "chakra", "manifest", "universe", "energy", "peace",
        ],
        "fitness": [
            "workout", "exercise", "gym", "fitness", "weight loss", "muscle", "training",
            "diet", "nutrition", "running", "cycling", "hiit", "cardio",
        ],
    }

    CATEGORY_SENTIMENT: Dict[str, float] = {
        "dark_content": -1.0,
        "motivational": 0.8,
        "entertainment": 0.5,
        "educational": 0.6,
        "music": 0.3,
        "romantic_sad": -0.2,
        "gaming": 0.2,
        "news": -0.1,
        "spiritual": 0.7,
        "fitness": 0.7,
        "uncategorized": 0.0,
    }

    def _classify_video(self, title: str) -> str:
        title_lower = title.lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in title_lower for kw in keywords):
                return category
        return "uncategorized"

    def parse_watch_history(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "lxml")
        videos = []

        content_cells = soup.find_all("div", class_="content-cell")
        for cell in content_cells:
            links = cell.find_all("a")
            if not links:
                continue

            title_link = links[0]
            title = title_link.get_text(strip=True)
            url = title_link.get("href", "")

            if not title or "Watched" not in cell.get_text():
                continue

            text = cell.get_text(separator="\n")
            lines = [l.strip() for l in text.split("\n") if l.strip()]

            timestamp = None
            for line in lines:
                if re.search(r"\d{4}", line) and ("AM" in line or "PM" in line or ":" in line):
                    timestamp = line
                    break

            category = self._classify_video(title)
            videos.append({
                "title": title,
                "url": url,
                "timestamp": timestamp,
                "category": category,
            })

        return videos

    def parse_search_history(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "lxml")
        searches = []

        content_cells = soup.find_all("div", class_="content-cell")
        for cell in content_cells:
            text = cell.get_text(strip=True)
            if "Searched for" not in text:
                continue

            links = cell.find_all("a")
            for link in links:
                query = link.get_text(strip=True)
                if query:
                    searches.append({
                        "query": query,
                        "category": self._classify_video(query),
                    })

        return searches

    def analyze(
        self,
        videos: List[Dict[str, Any]],
        searches: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not videos:
            return {
                "emotional_diet_score": 50,
                "category_breakdown": {},
                "dark_content_percentage": 0,
                "recovery_score": 50,
                "rumination_score": 0,
                "content_mood": "Neutral",
                "total_videos": 0,
                "insights": ["No video history found to analyze."],
            }

        searches = searches or []
        total = len(videos)

        category_counts: Dict[str, int] = {}
        for video in videos:
            cat = video.get("category", "uncategorized")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        category_breakdown = {
            cat: round((count / total) * 100, 1)
            for cat, count in category_counts.items()
        }

        dark_count = category_counts.get("dark_content", 0)
        dark_percentage = round((dark_count / total) * 100, 1)

        weighted_sentiment = 0.0
        for cat, count in category_counts.items():
            sentiment = self.CATEGORY_SENTIMENT.get(cat, 0.0)
            weighted_sentiment += sentiment * (count / total)

        emotional_diet_score = round((weighted_sentiment + 1) / 2 * 100)
        emotional_diet_score = max(0, min(100, emotional_diet_score))

        positive_cats = ["motivational", "educational", "spiritual", "fitness"]
        positive_ratio = sum(category_counts.get(c, 0) for c in positive_cats) / total
        recovery_score = round(positive_ratio * 100)

        negative_cats = ["dark_content", "romantic_sad"]
        negative_ratio = sum(category_counts.get(c, 0) for c in negative_cats) / total
        rumination_score = round(negative_ratio * 100)

        if emotional_diet_score >= 65:
            content_mood = "Positive & Growth-Oriented"
        elif emotional_diet_score >= 45:
            content_mood = "Balanced"
        elif emotional_diet_score >= 30:
            content_mood = "Slightly Negative"
        else:
            content_mood = "Concerning — Negative Content Heavy"

        insights = []
        if dark_percentage > 30:
            insights.append(f"High dark content consumption ({dark_percentage}%) — may impact mood negatively.")
        if recovery_score > 40:
            insights.append(f"Good balance of uplifting content ({recovery_score}% positive).")
        if category_counts.get("educational", 0) / total > 0.2:
            insights.append("Strong educational content consumption — positive for mental stimulation.")
        if category_counts.get("music", 0) / total > 0.3:
            insights.append("Heavy music consumption detected — consider content diversity.")
        if rumination_score > 25:
            insights.append("Elevated rumination patterns detected in viewing habits.")
        if not insights:
            insights.append("Your content diet appears balanced overall.")

        return {
            "emotional_diet_score": emotional_diet_score,
            "category_breakdown": category_breakdown,
            "dark_content_percentage": dark_percentage,
            "recovery_score": recovery_score,
            "rumination_score": rumination_score,
            "content_mood": content_mood,
            "total_videos": total,
            "total_searches": len(searches),
            "insights": insights,
        }
