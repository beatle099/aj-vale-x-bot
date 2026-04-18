"""JSON-backed post history and near-duplicate detection."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)


@dataclass
class HistoryItem:
    text: str
    trigger: str
    score: float
    created_at: str
    metadata: Dict[str, Any]


class HistoryStore:
    def __init__(self, path: str | Path = "post_history.json", threshold: float = 0.82) -> None:
        self.path = Path(path)
        self.threshold = threshold
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[HistoryItem]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return [HistoryItem(**item) for item in raw]
        except (json.JSONDecodeError, TypeError) as exc:
            LOGGER.warning("Could not read history %s: %s", self.path, exc)
            return []

    def save(self, items: List[HistoryItem]) -> None:
        self.path.write_text(
            json.dumps([asdict(item) for item in items], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add(self, text: str, trigger: str, score: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        items = self.load()
        items.append(
            HistoryItem(
                text=text,
                trigger=trigger,
                score=score,
                created_at=datetime.now(timezone.utc).isoformat(),
                metadata=metadata or {},
            )
        )
        self.save(items)

    def similarity(self, text: str) -> float:
        normalized = " ".join(text.lower().split())
        best = 0.0
        for item in self.load():
            candidate = " ".join(item.text.lower().split())
            best = max(best, SequenceMatcher(None, normalized, candidate).ratio())
        return round(best, 3)

    def is_duplicate(self, text: str) -> bool:
        return self.similarity(text) >= self.threshold
