"""CLI and optional FastAPI webhook for the A.J. Vale X draft bot."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

from history_store import HistoryStore
from trigger_router import TriggerRouter
from x_client import XClient


def load_env(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def read_payload(args: argparse.Namespace) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if args.payload:
        payload.update(json.loads(Path(args.payload).read_text(encoding="utf-8")))
    if args.json:
        payload.update(json.loads(args.json))
    if args.trigger:
        payload["trigger"] = args.trigger
    if args.title:
        payload["title"] = args.title
    if args.note:
        payload["note"] = args.note
    if args.review_excerpt:
        payload["review_excerpt"] = args.review_excerpt
    return payload


def build_router() -> TriggerRouter:
    history_path = os.getenv("HISTORY_PATH", "post_history.json")
    threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.82"))
    return TriggerRouter(history=HistoryStore(history_path, threshold=threshold))


def run_cli() -> None:
    load_env()
    configure_logging()

    parser = argparse.ArgumentParser(description="Generate A.J. Vale X/Twitter post drafts.")
    parser.add_argument("--trigger", help="Trigger name, e.g. persona_post or book_echo")
    parser.add_argument("--title", help="Catalog title or alias")
    parser.add_argument("--note", help="Manual note, observation, or rough thought")
    parser.add_argument("--review-excerpt", help="Reader review excerpt for review_reflection")
    parser.add_argument("--payload", help="Path to JSON payload")
    parser.add_argument("--json", help="Inline JSON payload")
    parser.add_argument("--persist", action="store_true", help="Save the recommended draft to local history")
    parser.add_argument("--post", action="store_true", help="Post recommended tweet if env allows it")
    parser.add_argument("--webhook", action="store_true", help="Run optional FastAPI webhook")
    args = parser.parse_args()

    if args.webhook:
        run_webhook()
        return

    payload = read_payload(args)
    if "trigger" not in payload:
        parser.error("--trigger or payload.trigger is required")

    result = build_router().handle(payload, persist_recommended=args.persist)
    if args.post:
        dry_run = bool_env("DRY_RUN", True)
        auto_post = bool_env("AUTO_POST", False)
        result["post_result"] = XClient(dry_run=dry_run, auto_post=auto_post).post_tweet(
            result["recommended_tweet"]["text"]
        )

    print(json.dumps(result, indent=2, ensure_ascii=False))


def create_app():
    load_env()
    configure_logging()
    try:
        from fastapi import FastAPI, HTTPException
    except ImportError as exc:
        raise RuntimeError("FastAPI webhook requires: pip install fastapi uvicorn") from exc

    app = FastAPI(title="A.J. Vale X Draft Bot")

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/generate")
    def generate(payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return build_router().handle(payload, persist_recommended=bool(payload.get("persist")))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


def run_webhook() -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("Webhook mode requires: pip install fastapi uvicorn") from exc
    uvicorn.run("main:create_app", factory=True, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))


if __name__ == "__main__":
    run_cli()
