"""Route incoming trigger payloads into scored, de-duplicated tweet drafts."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from history_store import HistoryStore
from post_generator import Draft, PostGenerator
from prompts import TRIGGER_INTENTS

LOGGER = logging.getLogger(__name__)


class TriggerRouter:
    def __init__(
        self,
        generator: Optional[PostGenerator] = None,
        history: Optional[HistoryStore] = None,
        max_retries: int = 3,
    ) -> None:
        self.generator = generator or PostGenerator()
        self.history = history or HistoryStore()
        self.max_retries = max_retries

    @property
    def supported_triggers(self) -> List[str]:
        return list(TRIGGER_INTENTS.keys())

    def handle(self, payload: Dict[str, Any], persist_recommended: bool = False) -> Dict[str, Any]:
        trigger = payload.get("trigger")
        if trigger not in TRIGGER_INTENTS:
            raise ValueError(f"Unsupported trigger '{trigger}'. Supported: {', '.join(self.supported_triggers)}")

        candidates: List[Draft] = []
        working_payload = dict(payload)
        for attempt in range(self.max_retries):
            working_payload["retry_nonce"] = attempt
            generated = self.generator.generate(trigger, working_payload)
            fresh = [draft for draft in generated if not self.history.is_duplicate(draft.text)]
            candidates = fresh or generated
            if fresh:
                break
            LOGGER.info("All generated drafts were near-duplicates on attempt %s", attempt + 1)

        options = candidates[:5]
        recommended = options[0]
        shorter = self._find_label(options, "shorter") or min(options, key=lambda item: len(item.text))
        literary = self._find_label(options, "more_literary") or recommended
        accessible = self._find_label(options, "more_accessible") or recommended
        history_similarity = self.history.similarity(recommended.text)

        if persist_recommended:
            self.history.add(
                recommended.text,
                trigger,
                recommended.score["total"],
                {"title": payload.get("title") or payload.get("book"), "source": "recommended"},
            )

        return {
            "trigger": trigger,
            "options": [asdict(option) for option in options],
            "recommended_tweet": asdict(recommended),
            "shorter_version": asdict(shorter),
            "more_literary_version": asdict(literary),
            "more_accessible_version": asdict(accessible),
            "optional_hashtag_line": recommended.hashtags,
            "history_similarity": history_similarity,
            "dry_run_note": "Draft generated only. Posting requires AUTO_POST=true and DRY_RUN=false.",
        }

    @staticmethod
    def _find_label(options: List[Draft], label: str) -> Optional[Draft]:
        return next((option for option in options if option.label == label), None)
