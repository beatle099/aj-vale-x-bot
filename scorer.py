"""Heuristic scoring for A.J. Vale X/Twitter drafts."""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, Iterable

from prompts import AVOID_PHRASES


DIMENSIONS = [
    "originality",
    "author_brand_fit",
    "elegance",
    "emotional_resonance",
    "curiosity_generation",
    "subtle_commercial_value",
    "non_promotional_quality",
]


@dataclass(frozen=True)
class Score:
    originality: float
    author_brand_fit: float
    elegance: float
    emotional_resonance: float
    curiosity_generation: float
    subtle_commercial_value: float
    non_promotional_quality: float

    @property
    def total(self) -> float:
        return round(sum(asdict(self).values()) / len(DIMENSIONS), 3)

    def as_dict(self) -> Dict[str, float]:
        data = asdict(self)
        data["total"] = self.total
        return data


BRAND_TERMS = {
    "machine",
    "city",
    "cities",
    "room",
    "judgment",
    "memory",
    "silence",
    "prophecy",
    "future",
    "world",
    "worlds",
    "spark",
    "eternity",
    "invented",
    "invention",
    "ruin",
    "conscience",
    "fear",
}

EMOTIONAL_TERMS = {
    "fear",
    "grief",
    "silence",
    "memory",
    "guilt",
    "beauty",
    "violence",
    "wonder",
    "dread",
    "mercy",
    "loneliness",
}


def _clamp(value: float) -> float:
    return round(max(0.0, min(10.0, value)), 2)


def _tokens(text: str) -> Iterable[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def score_tweet(text: str, title: str | None = None) -> Score:
    words = list(_tokens(text))
    unique_ratio = len(set(words)) / max(1, len(words))
    length = len(text)
    brand_hits = len(set(words) & BRAND_TERMS)
    emotional_hits = len(set(words) & EMOTIONAL_TERMS)
    question_bonus = 1.5 if "?" in text else 0.0
    title_bonus = 1.5 if title and title.lower() in text.lower() else 0.0
    hashtag_count = text.count("#")
    avoid_hits = sum(1 for phrase in AVOID_PHRASES if phrase in text.lower())
    hard_cta = bool(re.search(r"\b(buy|download|shop|click|subscribe)\b", text, re.I))
    cadence_bonus = 1.0 if any(mark in text for mark in [".", ";", ":"]) else 0.0

    return Score(
        originality=_clamp(5.0 + unique_ratio * 4.0 - avoid_hits * 2.0),
        author_brand_fit=_clamp(4.5 + brand_hits * 0.9 + title_bonus),
        elegance=_clamp(7.0 + cadence_bonus - max(0, length - 240) / 20 - hashtag_count * 0.4),
        emotional_resonance=_clamp(4.5 + emotional_hits * 1.0 + brand_hits * 0.25),
        curiosity_generation=_clamp(5.0 + question_bonus + brand_hits * 0.45),
        subtle_commercial_value=_clamp(4.0 + title_bonus + min(2.5, brand_hits * 0.35)),
        non_promotional_quality=_clamp(9.5 - avoid_hits * 3.0 - (2.0 if hard_cta else 0.0) - max(0, hashtag_count - 1)),
    )
