"""Minimal X API client with dry-run and disabled-by-default posting."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Dict

LOGGER = logging.getLogger(__name__)


class XClient:
    def __init__(self, bearer_token: str | None = None, dry_run: bool = True, auto_post: bool = False) -> None:
        self.bearer_token = bearer_token or os.getenv("X_BEARER_TOKEN")
        self.dry_run = dry_run
        self.auto_post = auto_post

    def post_tweet(self, text: str) -> Dict[str, Any]:
        if self.dry_run or not self.auto_post:
            LOGGER.info("DRY RUN: would post tweet: %s", text)
            return {"posted": False, "dry_run": True, "text": text}
        if not self.bearer_token:
            raise RuntimeError("X_BEARER_TOKEN is required when AUTO_POST=true and DRY_RUN=false")

        request = urllib.request.Request(
            "https://api.twitter.com/2/tweets",
            data=json.dumps({"text": text}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read().decode("utf-8")
                return {"posted": True, "response": json.loads(body)}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"X API request failed: {exc.code} {detail}") from exc
