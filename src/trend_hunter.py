from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta


DEFAULT_TOPICS = ["crypto startups"]

# These are intentionally populated from ZENO_MISSION_TOPIC at runtime.
# Keeping them empty by default prevents old non-Zeno topic drift.
MISSION_TERMS: set[str] = set()
MISSION_PHRASES: set[str] = set()

SHOPPING_TERMS = {
    "shopping",
    "shop",
    "store",
    "stores",
    "fashion",
    "clothing",
    "outfit",
    "dress",
    "shoes",
    "beauty",
    "makeup",
    "skincare",
    "product",
    "products",
    "order",
    "orders",
    "checkout",
    "cart",
    "coupon",
    "discount",
    "sale",
    "delivery",
    "returns",
    "exchange",
    "sizes",
}

SHOPPING_PHRASES = {
    "product info",
    "order support",
    "customer support",
    "customer service",
    "find a store",
    "store locator",
    "size guide",
    "new collection",
    "zeno sale",
    "buy now",
    "add to cart",
}


class TrendHunter:
    def __init__(self) -> None:
        self.configured_topics = self._configured_topics()
        self.topic_groups = {"configured": self.configured_topics}
        for topic in self.configured_topics:
            lowered = topic.lower()
            MISSION_PHRASES.add(lowered)
            MISSION_TERMS.update(re.findall(r"[a-z]{3,}", lowered))
        self.seed_topics = [item for values in self.topic_groups.values() for item in values]

    def _configured_topics(self) -> list[str]:
        raw = os.environ.get("ZENO_MISSION_TOPIC", "").strip()
        if not raw:
            raw = ",".join(DEFAULT_TOPICS)
        topics: list[str] = []
        seen = set()
        for item in re.split(r"[,;\n]+", raw):
            topic = " ".join(item.split()).strip()
            if not topic:
                continue
            key = topic.lower()
            if key in seen:
                continue
            seen.add(key)
            topics.append(topic)
        return topics[:12]

    def default_queries(self) -> list[str]:
        since = (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d")
        queries: list[str] = []
        for topic in self.configured_topics:
            safe_topic = topic.replace('"', "").strip()
            if not safe_topic:
                continue
            if " " in safe_topic:
                safe_topic = f'"{safe_topic}"'
            queries.extend(
                [
                    f"{safe_topic} min_faves:80 min_replies:10 lang:en since:{since}",
                    f"{safe_topic} filter:images min_faves:180 min_retweets:15 min_replies:12 lang:en since:{since}",
                    f"{safe_topic} filter:videos min_faves:220 min_retweets:20 min_replies:15 lang:en since:{since}",
                ]
            )
        return queries

    def parse_queries(self, raw: str) -> list[str]:
        try:
            parsed = json.loads(raw)
        except Exception:
            return []
        if not isinstance(parsed, list):
            return []
        queries: list[str] = []
        seen = set()
        for item in parsed:
            query = str(item or "").strip()
            if not query or query in seen:
                continue
            if not self._query_is_on_mission(query):
                continue
            seen.add(query)
            queries.append(query)
        return queries

    def _query_is_on_mission(self, query: str) -> bool:
        lowered = (query or "").lower()
        tokens = set(re.findall(r"[a-z]{3,}", lowered))
        has_mission_phrase = any(phrase in lowered for phrase in MISSION_PHRASES)
        if any(phrase in lowered for phrase in SHOPPING_PHRASES):
            return False
        if (tokens & SHOPPING_TERMS) and not has_mission_phrase:
            return False
        return bool((tokens & MISSION_TERMS) or has_mission_phrase)

    def compose_queries(self, memory_briefs: list[str], limit: int = 8) -> list[str]:
        since = (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d")
        queries: list[str] = []
        seen = set()

        def add(query: str) -> None:
            query = " ".join((query or "").split()).strip()
            if not query or query in seen:
                return
            seen.add(query)
            queries.append(query)

        for query in self.default_queries():
            add(query)

        boosted_topics: list[str] = []
        for item in memory_briefs:
            text = (item or "").strip().lower()
            if not text:
                continue
            for match in re.findall(r"[a-z]{4,}", text):
                if match in {"signal", "source", "trend", "memory", "posts", "fresh", "strongest", "ignored"}:
                    continue
                if match in SHOPPING_TERMS or match not in MISSION_TERMS:
                    continue
                boosted_topics.append(match)

        for index, topic in enumerate(boosted_topics[:12]):
            media_filter = "filter:videos" if index % 2 == 0 else "filter:images"
            add(f"{topic} {media_filter} min_faves:3000 min_retweets:220 min_replies:30 lang:en since:{since}")

        return queries[:limit]

    def fallback_results(self, queries: list[str]) -> list[dict]:
        results = []
        for query in queries[:6]:
            topic = query.split("min_", 1)[0].replace("lang:en", "").replace("since:", "").strip()
            results.append(
                {
                    "query": query,
                    "topic": topic,
                    "user": "trend-sim",
                    "text": f"{topic.title()} is shifting faster than most people realize. The strongest signal is still being ignored.",
                    "url": "",
                    "image_url": "",
                    "simulated": True,
                    "metrics": {"engagement_hint": 1200},
                }
            )
        return results
