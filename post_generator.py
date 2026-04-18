"""Local draft generator for A.J. Vale X/Twitter posts."""

from __future__ import annotations

import hashlib
import itertools
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from catalog import BRAND, CATALOG, Book, get_book
from prompts import SOFT_HASHTAGS, TRIGGER_INTENTS
from scorer import score_tweet


MAX_CHARS = 260


@dataclass
class Draft:
    label: str
    text: str
    score: Dict[str, float]
    rationale: str
    hashtags: str = ""


def _seed(payload: Dict[str, Any]) -> random.Random:
    key = repr(sorted(payload.items())).encode("utf-8", errors="ignore")
    return random.Random(hashlib.sha256(key).hexdigest())


def _trim(text: str, max_chars: int = MAX_CHARS) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_chars:
        return cleaned
    cut = cleaned[: max_chars - 1].rsplit(" ", 1)[0].rstrip(".,;:")
    return f"{cut}."


def _pick_book(payload: Dict[str, Any], rng: random.Random) -> Book:
    requested = get_book(payload.get("title") or payload.get("book"))
    return requested or rng.choice(CATALOG)


def _soft_hashtag(trigger: str, rng: random.Random) -> str:
    if trigger in {"writing_update", "book_echo", "launch_whisper"}:
        return rng.choice(SOFT_HASHTAGS[:3])
    if trigger == "reader_question":
        return ""
    return rng.choice(["", "", "#SpeculativeFiction"])


def _rationale(trigger: str, text: str, title: Optional[str]) -> str:
    reason = TRIGGER_INTENTS.get(trigger, "matches the A.J. Vale voice")
    title_note = f" It lets {title} echo as mythology instead of inventory." if title and title in text else ""
    return f"Works because it matches the trigger intent: {reason}. It stays non-promotional.{title_note}"


class PostGenerator:
    def generate(self, trigger: str, payload: Optional[Dict[str, Any]] = None) -> List[Draft]:
        payload = payload or {}
        rng = _seed({"trigger": trigger, **payload})
        book = _pick_book(payload, rng)
        note = payload.get("note") or payload.get("text") or payload.get("observation") or ""
        review = payload.get("review_excerpt") or payload.get("reader_reaction") or ""

        factories = {
            "persona_post": self._persona,
            "mood_post": self._mood,
            "book_echo": self._book_echo,
            "reader_question": self._reader_question,
            "writing_update": self._writing_update,
            "launch_whisper": self._launch_whisper,
            "review_reflection": self._review_reflection,
            "cultural_observation": self._cultural_observation,
            "manual_note": self._manual_note,
        }
        factory = factories.get(trigger)
        if not factory:
            raise ValueError(f"Unsupported trigger: {trigger}")

        raw = factory(book, note=note, review=review, payload=payload, rng=rng)
        retry_nonce = int(payload.get("retry_nonce", 0) or 0)
        if retry_nonce:
            raw = [(label, self._retry_variation(text, retry_nonce)) for label, text in raw]
        drafts: List[Draft] = []
        for label, text in raw:
            tweet = _trim(text)
            score = score_tweet(tweet, title=book.title).as_dict()
            hashtag = _soft_hashtag(trigger, rng)
            drafts.append(
                Draft(
                    label=label,
                    text=tweet,
                    score=score,
                    hashtags=hashtag,
                    rationale=_rationale(trigger, tweet, book.title),
                )
            )
        return sorted(drafts, key=lambda draft: draft.score["total"], reverse=True)

    @staticmethod
    def _retry_variation(text: str, retry_nonce: int) -> str:
        """Shift framing when history rejects a draft as too similar."""
        replacement_sets = [
            {
                "silence": "quiet",
                "city": "public world",
                "cities": "public worlds",
                "machine": "system",
                "room": "threshold",
                "future": "coming century",
            },
            {
                "silence": "withheld answer",
                "city": "civil order",
                "cities": "civil orders",
                "machine": "apparatus",
                "room": "inner architecture",
                "future": "tomorrow",
            },
            {
                "silence": "pause",
                "city": "map",
                "cities": "maps",
                "machine": "engine",
                "room": "doorway",
                "future": "next age",
            },
        ]
        replacements = replacement_sets[(retry_nonce - 1) % len(replacement_sets)]
        varied = text
        for old, new in replacements.items():
            varied = varied.replace(old, new).replace(old.capitalize(), new.capitalize())
        return varied

    def _persona(self, book: Book, **_: Any) -> List[tuple[str, str]]:
        return [
            ("primary", "I keep returning to the moment a civilization learns to hide panic inside procedure."),
            ("shorter", "Order is often panic with better architecture."),
            ("more_literary", "A city does not become innocent by lowering its voice. It only teaches guilt to wear clean walls."),
            ("more_accessible", "The frightening thing is not collapse. It is how normal collapse can look from the sidewalk."),
            ("catalog_bridge", f"Somewhere behind {book.title}, I keep hearing the same question: what survives when meaning becomes managed?"),
        ]

    def _mood(self, book: Book, **_: Any) -> List[tuple[str, str]]:
        return [
            ("primary", "The future does not always arrive as a disaster. Sometimes it arrives as a form everyone learns to sign."),
            ("shorter", "The future may arrive as paperwork."),
            ("more_literary", "There are ruins that still have electricity, elevators, clean windows, and a committee for every scream."),
            ("more_accessible", "Some systems do not look cruel until you notice what they have taught everyone to stop asking."),
            ("catalog_bridge", f"{book.title} began, for me, as an atmosphere before it became a title."),
        ]

    def _book_echo(self, book: Book, **_: Any) -> List[tuple[str, str]]:
        motif = book.motifs[0] if book.motifs else "memory"
        return [
            ("primary", f"{book.title} is less a title than a pressure in the room: {book.atmosphere}."),
            ("shorter", f"{book.title}: a name for the silence after {motif} becomes unavoidable."),
            ("more_literary", f"I think of {book.title} as a door left open by a century that no longer trusts its own explanations."),
            ("more_accessible", f"The idea behind {book.title} is simple: the world can seem orderly and still be hiding a wound."),
            ("catalog_bridge", f"Before {book.title} was a book, it was a question I could not make leave quietly."),
        ]

    def _reader_question(self, book: Book, **_: Any) -> List[tuple[str, str]]:
        terms = list(itertools.islice(itertools.cycle(book.motifs or ["memory"]), 3))
        return [
            ("primary", f"Which is more dangerous: {terms[0]}, {terms[1]}, or the silence that lets both continue?"),
            ("shorter", "What does a person become after they stop expecting an answer?"),
            ("more_literary", "If a room remembers what a person refuses to confess, is the room haunted or honest?"),
            ("more_accessible", "When does a system become more believable than the people trapped inside it?"),
            ("catalog_bridge", f"What kind of reader enters {book.title} looking for a plot and leaves thinking about judgment?"),
        ]

    def _writing_update(self, book: Book, **_: Any) -> List[tuple[str, str]]:
        return [
            ("primary", f"Working inside the world of {book.title} today. The pages are less interested in answers than in the exact temperature of dread."),
            ("shorter", f"Back inside {book.title}. The silence is doing most of the work."),
            ("more_literary", f"Editing {book.title} feels like walking through a lit corridor while something behind the walls revises its breathing."),
            ("more_accessible", f"Writing today is mostly listening: to the room, the city, the machine, and what each one refuses to explain."),
            ("catalog_bridge", f"The catalog keeps forming a pattern: rooms, machines, cities, whispers. Different doors. Similar pressure."),
        ]

    def _launch_whisper(self, book: Book, **_: Any) -> List[tuple[str, str]]:
        return [
            ("primary", f"{book.title} has opened its door. I prefer to let the room speak before I explain why it was built."),
            ("shorter", f"{book.title} is now part of the open world."),
            ("more_literary", f"A new threshold is open: {book.title}. Enter quietly. The walls are listening for the question you bring."),
            ("more_accessible", f"{book.title} is out in the world now. No loud announcement, just a door left open."),
            ("catalog_bridge", f"For readers tracing the rooms, machines, cities, and whispers: {book.title} is another signal in the pattern."),
        ]

    def _review_reflection(self, book: Book, review: str = "", **_: Any) -> List[tuple[str, str]]:
        fragment = review.strip().strip('"')[:90] or "unsettling"
        return [
            ("primary", f"A reader called the feeling '{fragment}'. That interests me because the book was never meant to comfort the room. It was meant to reveal it."),
            ("shorter", f"When a reader says {book.title} stayed with them, I wonder what part refused to leave."),
            ("more_literary", f"The most useful reactions are not applause. They are small disturbances in the reader's private weather."),
            ("more_accessible", f"I pay attention when a reader remembers the atmosphere more than the plot. That means the world followed them out."),
            ("catalog_bridge", f"{book.title} seems to leave readers with a question, which is closer to the point than any answer I could give."),
        ]

    def _cultural_observation(self, book: Book, note: str = "", **_: Any) -> List[tuple[str, str]]:
        detail = note.strip() or "a crowd moving through a bright public space without looking at one another"
        return [
            ("primary", f"I saw {detail}. The modern world often looks most fictional when nobody is pretending."),
            ("shorter", "The city was calm in the way a sealed record is calm."),
            ("more_literary", "Public silence has a texture. Some days it feels designed, installed, maintained."),
            ("more_accessible", "A city can look efficient and still feel like everyone inside it has agreed not to name the same fear."),
            ("catalog_bridge", f"That is the atmosphere I keep finding near {book.title}: ordinary surfaces, extraordinary pressure."),
        ]

    def _manual_note(self, book: Book, note: str = "", **_: Any) -> List[tuple[str, str]]:
        base = note.strip() or "meaning is harder to finish than work"
        return [
            ("primary", f"{base.rstrip('.')}. That is where the story begins: not with an event, but with the pressure it leaves behind."),
            ("shorter", f"{base.rstrip('.')}. The rest is atmosphere."),
            ("more_literary", f"{base.rstrip('.')}; a thought like a locked room, still warm from whoever left it."),
            ("more_accessible", f"{base.rstrip('.')}. I keep writing toward the moment that truth becomes impossible to ignore."),
            ("catalog_bridge", f"{base.rstrip('.')}. Somewhere near {book.title}, that thought becomes a door."),
        ]
