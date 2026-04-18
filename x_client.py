"""Minimal X API client with dry-run and disabled-by-default posting."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict

LOGGER = logging.getLogger(__name__)


class XClient:
    def __init__(
        self,
        bearer_token: str | None = None,
        dry_run: bool = True,
        auto_post: bool = False,
        api_key: str | None = None,
        api_secret: str | None = None,
        access_token: str | None = None,
        access_token_secret: str | None = None,
    ) -> None:
        self.bearer_token = bearer_token or os.getenv("X_BEARER_TOKEN")
        self.api_key = api_key or os.getenv("X_API_KEY")
        self.api_secret = api_secret or os.getenv("X_API_SECRET")
        self.access_token = access_token or os.getenv("X_ACCESS_TOKEN")
        self.access_token_secret = access_token_secret or os.getenv("X_ACCESS_TOKEN_SECRET")
        self.dry_run = dry_run
        self.auto_post = auto_post

    def post_tweet(self, text: str) -> Dict[str, Any]:
        if self.dry_run or not self.auto_post:
            LOGGER.info("DRY RUN: would post tweet: %s", text)
            return {"posted": False, "dry_run": True, "text": text}

        headers = {"Content-Type": "application/json"}
        if self._has_oauth1_credentials:
            headers["Authorization"] = self._oauth1_header(
                method="POST",
                url="https://api.x.com/2/tweets",
            )
        elif self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        else:
            raise RuntimeError(
                "Posting requires X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, and "
                "X_ACCESS_TOKEN_SECRET, or a user-context X_BEARER_TOKEN."
            )

        payload = json.dumps({"text": text}).encode("utf-8")
        request = urllib.request.Request(
            "https://api.x.com/2/tweets",
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read().decode("utf-8")
                return {"posted": True, "response": json.loads(body)}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"X API request failed: {exc.code} {detail}") from exc

    @property
    def _has_oauth1_credentials(self) -> bool:
        return all([self.api_key, self.api_secret, self.access_token, self.access_token_secret])

    def _oauth1_header(self, method: str, url: str) -> str:
        if not self._has_oauth1_credentials:
            raise RuntimeError("OAuth 1.0a credentials are incomplete")

        oauth_params = {
            "oauth_consumer_key": self.api_key or "",
            "oauth_nonce": uuid.uuid4().hex,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": self.access_token or "",
            "oauth_version": "1.0",
        }
        encoded_params = urllib.parse.urlencode(sorted(oauth_params.items()), quote_via=urllib.parse.quote)
        base_parts = [
            method.upper(),
            urllib.parse.quote(url, safe=""),
            urllib.parse.quote(encoded_params, safe=""),
        ]
        signature_base = "&".join(base_parts)
        signing_key = "&".join(
            [
                urllib.parse.quote(self.api_secret or "", safe=""),
                urllib.parse.quote(self.access_token_secret or "", safe=""),
            ]
        )
        digest = hmac.new(signing_key.encode("utf-8"), signature_base.encode("utf-8"), hashlib.sha1).digest()
        oauth_params["oauth_signature"] = base64.b64encode(digest).decode("utf-8")
        header_params = ", ".join(
            f'{urllib.parse.quote(key, safe="")}="{urllib.parse.quote(value, safe="")}"'
            for key, value in sorted(oauth_params.items())
        )
        return f"OAuth {header_params}"
